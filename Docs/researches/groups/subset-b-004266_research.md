<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/xilinx_sdfec.c -->
# sources/distributed-fs/ceph-client/drivers/misc/xilinx_sdfec.c

## Purpose
Implements the platform misc character driver for Xilinx SD-FEC16 soft-decision forward error correction IP. It maps the IP register bank, enables required clocks, parses device-tree stream/FEC configuration, exposes `/dev/xsdfecN`, and lets userspace start/stop the engine, configure Turbo or LDPC parameters, manage interrupts, poll error events, and read/clear error counters.

## Important APIs, Types, And Functions
- `struct xsdfec_dev` owns the misc device, clock handles, register base, cached `struct xsdfec_config`, wait queue, device state, IRQ state, and ISR/ECC counters.
- `struct xsdfec_clks` tracks core, AXI-lite, stream, control, and status clocks.
- `xsdfec_dev_ioctl()` dispatches UAPI commands from `<uapi/misc/xilinx_sdfec.h>` including `XSDFEC_START_DEV`, `XSDFEC_STOP_DEV`, `XSDFEC_GET_STATUS`, `XSDFEC_GET_CONFIG`, `XSDFEC_SET_IRQ`, `XSDFEC_SET_TURBO`, `XSDFEC_ADD_LDPC_CODE_PARAMS`, `XSDFEC_SET_ORDER`, `XSDFEC_SET_BYPASS`, and stats operations.
- LDPC programming is split across `xsdfec_reg0_write()` through `xsdfec_reg3_write()` plus `xsdfec_table_write()` for SC/LA/QC tables copied from pinned userspace pages.
- `xsdfec_irq_thread()` masks interrupts, reads and clears ISR/ECC status, updates error counters and state, wakes poll waiters, then unmasks interrupts.
- `xsdfec_parse_of()`, `xsdfec_clk_init()`, `xsdfec_probe()`, and `xsdfec_remove()` integrate with the platform-driver lifecycle and the `xlnx,sd-fec-1.1` compatible.

## Control Flow
Probe allocates `xsdfec_dev`, enables clocks, maps MMIO, optionally obtains an IRQ, parses required device-tree properties, mirrors hardware state into `config`, registers a threaded IRQ, allocates an ID, and registers a dynamic misc device. Userspace opens the misc node and drives the device through ioctl calls. Start validates that the hardware FEC code register matches the configured LDPC/Turbo mode, then enables all AXI stream interfaces. Stop clears only input AXI stream enables and marks the device stopped. LDPC setup is refused for Turbo devices, started devices, or write-protected code memories; validated register fields and user tables are then written into the hardware address windows.

## State And Persistence
Persistent state is hardware register state plus the in-memory cached configuration and counters. Error counters (`isr_err_count`, `cecc_count`, `uecc_count`) persist until `XSDFEC_CLEAR_STATS` or driver removal. `state_updated` and `stats_updated` are edge flags consumed by poll/status/stat reads. Device IDs are allocated from a global IDA. No on-disk state is written.

## Dependencies And Integration Points
Depends on platform devices, OF properties (`xlnx,sdfec-code`, `xlnx,sdfec-din-words`, stream widths, output word settings), the common clock framework, MMIO accessors, miscdevice, wait queues, threaded IRQs, user-copy helpers, `pin_user_pages_fast()`, and the SDFEC UAPI header. It integrates with userspace through `/dev/xsdfecN`, `poll()`, and ioctl structures.

## Risks And Edge Cases
LDPC table writes pin userspace pages and assume table length/offset arithmetic remains within hardware depth. IRQ masking/unmasking must match the hardware semantics where interrupt mask registers read as masked bits. The source snapshot contains apparent syntax/duplication defects in the shown file, including extra braces near `update_bool_config_from_reg()` and `xsdfec_table_write()`, a duplicated `XSDFEC_GET_TURBO` call, and a duplicated `IS_ERR(clks->dout_clk)` line; these would be compile-blocking or cleanup targets if present in the active build. Optional clocks are stored as `NULL`, so enable/disable paths rely on clock helpers tolerating null handles or need guarding depending on kernel API behavior.

## Test Signals
Build with `CONFIG_XILINX_SDFEC` and run sparse/smatch for user-copy and MMIO paths. Probe should create `/dev/xsdfecN` on a matching DT node with all required properties. Useful runtime checks include ioctl start/stop/config/stat round trips, poll wakeups on injected ISR/ECC events, LDPC range validation failures, and clock/IRQ unwind tests on forced probe failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/xilinx_sdfec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/xilinx_tmr_inject.c -->
# sources/distributed-fs/ceph-client/drivers/misc/xilinx_tmr_inject.c

## Purpose
Provides a platform driver for Xilinx Triple Modular Redundancy Inject IP. The driver programs the injection hardware and exposes a debugfs fault-injection control so developers can trigger MicroBlaze TMR error injection paths.

## Important APIs, Types, And Functions
- `struct xtmr_inject_dev` stores the MMIO register base and validated magic value.
- `xtmr_inject_write()` and `xtmr_inject_read()` are local MMIO accessors.
- `xtmr_inject_set()` is the debugfs write callback; only value `1` is accepted and it calls `xmb_inject_err()`.
- `xtmr_inject_init()` applies optional fault-injection attributes, enables injection in the control register, and programs address/instruction injection registers from `XMB_INJECT_ERR_OFFSET`.
- `xtmr_init_debugfs()` creates `/sys/kernel/debug/xtmr_inject/inject_fault/...` entries.
- `xtmr_inject_probe()` validates `xlnx,magic`, maps registers, initializes hardware, and stores driver data.

## Control Flow
On probe, the driver allocates private data, maps the platform resource, reads and range-checks `xlnx,magic`, programs the TMR Inject control/address registers, creates debugfs controls, and binds the state to the platform device. A debugfs write of `1` routes directly to `xmb_inject_err()`, which is provided by the Xilinx MicroBlaze manager support. Remove recursively deletes the debugfs root.

## State And Persistence
The only in-kernel persistent state is the mapped register pointer, magic value, global debugfs root, and the optional fault-injection attribute state. Hardware state persists in TMR Inject registers until reprogrammed or reset. No disk state is stored.

## Dependencies And Integration Points
Depends on OF/platform probing, MMIO helpers, `linux/fault-inject.h`, debugfs, and `asm/xilinx_mb_manager.h`. It integrates with the MicroBlaze TMR manager through `xmb_inject_err()` and shared injection offsets.

## Risks And Edge Cases
Debugfs controls intentionally expose fault injection, so production systems should treat this as a privileged diagnostic surface. The global `dbgfs_root` assumes one active instance; multiple matching devices would share/overwrite the same debugfs pointer. `fault_create_debugfs_attr()` failures are not checked, so missing debugfs entries may not fail probe. Invalid magic values are rejected above 255.

## Test Signals
Kernel build with the target architecture headers is the first signal. Runtime validation includes a matching `xlnx,tmr-inject-1.0` node, debugfs directory creation, register writes visible in hardware traces, rejection of debugfs values other than `1`, and expected TMR manager error-counter changes after injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/xilinx_tmr_inject.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/xilinx_tmr_manager.c -->
# sources/distributed-fs/ceph-client/drivers/misc/xilinx_tmr_manager.c

## Purpose
Implements the platform driver for Xilinx Triple Modular Redundancy Manager IP. It initializes TMR recovery control registers, registers callbacks used by the MicroBlaze break/error handler, and exposes minimal sysfs controls/statistics.

## Important APIs, Types, And Functions
- `struct xtmr_manager_dev` stores MMIO base, cached control-register value, magic value, error counter, and physical base address.
- `xtmr_manager_init()` disables SEM interrupt masking, enables recovery reset, sets break-delay behavior, marks break blocking in `cr_val`, and calls `xmb_manager_register()`.
- `xmb_manager_update_errcnt()` increments the software error counter from the registered callback.
- `xmb_manager_reset_handler()` clears the fault flag register during recovery.
- `errcnt_show()` exposes the accumulated count; `dis_block_break_store()` clears the block-break bit and writes the control register.
- `xtmr_manager_probe()` maps registers, validates `xlnx,magic1`, initializes hardware, and binds device data.

## Control Flow
Probe allocates state, maps the register resource while capturing the physical base, reads the required magic property, validates it, calls the init routine, and registers sysfs groups through the platform driver's `.dev_groups`. The MicroBlaze break path later invokes registered callbacks to count errors and clear manager fault state. Userspace can read `errcnt` or write `dis_block_break` to unblock the break signal after handling.

## State And Persistence
State is held in hardware control/fault registers and the in-memory `err_cnt`. `cr_val` caches desired control bits for reuse by sysfs and registered break handling. Counters reset on driver reload or reboot. No persistent storage is used.

## Dependencies And Integration Points
Depends on OF/platform infrastructure, MMIO accessors, sysfs attribute groups, and `asm/xilinx_mb_manager.h`. It is tightly coupled to MicroBlaze TMR break handling through `xmb_manager_register()`, which receives the physical manager base, cached CR value, error-count callback, private data, and reset callback.

## Risks And Edge Cases
The sysfs `dis_block_break` parser accepts a hex value but does not use it except as a syntactic gate, so any parseable input clears the block-break bit. Error counter updates are not synchronized; if callbacks can race with sysfs reads or other callbacks, the count is approximate. Magic values above 255 are rejected, but other board-level register mismatches are only observable at runtime.

## Test Signals
Probe should succeed only with a valid `xlnx,tmr-manager-1.0` node and `xlnx,magic1 <= 255`. Runtime tests should verify expected control-register writes, `errcnt` increments after TMR injection, `dis_block_break` changes CR bits, and the reset callback clears the fault flag register.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/xilinx_tmr_manager.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/mmc/Kconfig

## Purpose
Defines the top-level kernel configuration entry for MMC, SD, and SDIO card support and includes the core and host-controller submenus.

## Important APIs, Types, And Functions
- `menuconfig MMC` is a tristate gated by `HAS_IOMEM`.
- When `MMC` is enabled, it sources `drivers/mmc/core/Kconfig` and `drivers/mmc/host/Kconfig`.

## Control Flow
Kconfig first presents the parent MMC option. If enabled as built-in or module, the nested core and host-driver Kconfig files become visible and can select block, crypto, pwrseq, test, SDIO UART, and hardware controller support.

## State And Persistence
The file contributes compile-time configuration state through `.config`; it has no runtime state. The selected symbol controls whether the core directory is built and whether host support is reachable.

## Dependencies And Integration Points
Depends on generic Kconfig, the `HAS_IOMEM` architecture capability, the MMC core Kconfig file, and the host-controller Kconfig tree.

## Risks And Edge Cases
Disabling `MMC` hides all child drivers even if board files or DT nodes exist. Because the top-level symbol is tristate, built-in versus module choices influence link order, hotplug behavior, and availability during early boot/rootfs mounting.

## Test Signals
Configuration tests should confirm `CONFIG_MMC=y/m` exposes expected child symbols and `CONFIG_MMC=n` excludes the core and host builds. Kernel build logs should show the core and host directories only when expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/mmc/Makefile

## Purpose
Routes top-level MMC build output into the core and host subdirectories.

## Important APIs, Types, And Functions
- `obj-$(CONFIG_MMC) += core/` builds the MMC core when the parent symbol is enabled.
- `obj-$(subst m,y,$(CONFIG_MMC)) += host/` descends into host drivers for both built-in and modular MMC configurations.

## Control Flow
Kbuild evaluates `CONFIG_MMC`; the core is built according to the actual tristate value, while the host directory is entered whenever MMC is enabled so individual host-driver objects can make their own built-in/module decisions.

## State And Persistence
Only build graph state is affected. No runtime or persistent state exists.

## Dependencies And Integration Points
Integrates with Kbuild's recursive object directory mechanism and the child Makefiles under `drivers/mmc/core` and `drivers/mmc/host`.

## Risks And Edge Cases
The `subst m,y` pattern is intentional: host-driver modules still need the directory visited when the core is modular. Build regressions here can silently omit all MMC hosts or the block driver.

## Test Signals
Check `make drivers/mmc/` output for descent into `core/` and `host/` under `CONFIG_MMC=y` and `CONFIG_MMC=m`, and no MMC object output when disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/mmc/core/Kconfig

## Purpose
Defines build-time options for MMC core adjuncts: power sequencing drivers, the block device driver, minor allocation, SDIO UART support, the destructive MMC test driver, and inline crypto support.

## Important APIs, Types, And Functions
- `PWRSEQ_EMMC`, `PWRSEQ_SD8787`, and `PWRSEQ_SIMPLE` select OF-based power/reset sequencing helpers.
- `MMC_BLOCK` enables the block device driver and depends on `BLOCK` plus RPMB compatibility.
- `MMC_BLOCK_MINORS` sets minors per MMC block disk, constrained to 4-256.
- `SDIO_UART` enables an SDIO UART/GPS class driver when TTY is present.
- `MMC_TEST` enables a debug/test driver that overwrites media.
- `MMC_CRYPTO` enables MMC crypto engine support when `BLK_INLINE_ENCRYPTION` is present.

## Control Flow
These symbols are visible under the parent `MMC` menu. Their values are consumed by the core Makefile to include power sequencing objects, `mmc_block`, debug/test modules, SDIO UART, and `crypto.o`.

## State And Persistence
The file only defines `.config` state. At runtime, selected options determine exposed block devices, debug/test surfaces, power sequencing behavior, and inline-encryption hooks.

## Dependencies And Integration Points
Integrates with OF, block layer, RPMB subsystem, TTY, block inline encryption, and Kbuild. Defaults for pwrseq helpers and `MMC_BLOCK` mean most MMC-capable kernels will include core card and filesystem support unless explicitly disabled.

## Risks And Edge Cases
`MMC_TEST` is destructive by design and should not be enabled casually. Too-small or too-large `MMC_BLOCK_MINORS` changes how many partitions/devices can be represented under the fixed major. `MMC_CRYPTO` only wires core support; host capabilities still determine whether encryption is usable.

## Test Signals
Config matrix builds should cover `MMC_BLOCK=y/m/n`, `MMC_CRYPTO=y/n` with `BLK_INLINE_ENCRYPTION`, and pwrseq modules. Runtime signals include expected `mmcblk*` nodes, pwrseq probing from DT, and absence of destructive test files unless `MMC_TEST` is selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/Makefile -->
# sources/distributed-fs/ceph-client/drivers/mmc/core/Makefile

## Purpose
Defines the MMC core and related module object composition for Kbuild.

## Important APIs, Types, And Functions
- `mmc_core-y` aggregates core bus, host, MMC/SD/SDIO protocol, UHS-II, GPIO slot, and regulator support.
- `mmc_core-$(CONFIG_OF) += pwrseq.o` adds OF power sequencing.
- `mmc_core-$(CONFIG_DEBUG_FS) += debugfs.o` adds debugfs support.
- `mmc_core-$(CONFIG_MMC_CRYPTO) += crypto.o` adds inline crypto hooks.
- `mmc_block-objs := block.o queue.o` builds the block driver from block and queue code.
- Separate objects cover pwrseq helpers, `mmc_test`, and `sdio_uart`.

## Control Flow
Kbuild links selected objects into `mmc_core.o`, `mmc_block.o`, and optional modules according to the corresponding Kconfig symbols. Built-in/module state follows each `obj-$(CONFIG_...)` assignment.

## State And Persistence
The Makefile has no runtime state; it controls which object code exists in the kernel image or modules.

## Dependencies And Integration Points
Integrates core code across `core.c`, `bus.c`, `host.c`, protocol-specific files, GPIO/regulator helpers, debugfs, block queueing, and optional pwrseq/test/UART/crypto code.

## Risks And Edge Cases
Object omission causes unresolved symbols or missing runtime features. Because `mmc_block` explicitly combines `block.o` and `queue.o`, API changes between those files need synchronized builds.

## Test Signals
Build logs and `modinfo` should show expected modules under relevant configs. Link failures, unresolved exports, or missing `mmc_core` debugfs/crypto behavior indicate composition drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/block.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/core/block.c

## Purpose
Implements the MMC/SD block device driver (`mmcblk`). It turns discovered MMC/SD cards into Linux block disks, handles read/write/flush/discard/secure erase requests, routes raw MMC ioctls, manages eMMC hardware partitions and RPMB character devices, performs request recovery, and exposes selected sysfs/debugfs controls.

## Important APIs, Types, And Functions
- `struct mmc_blk_data` owns a gendisk, `struct mmc_queue`, partition/RPMB lists, flags for CMD23/reliable writes, read-only state, active partition cache, and debugfs dentries.
- `struct mmc_rpmb_data` owns RPMB character-device state and registration with the RPMB framework.
- `mmc_blk_probe()`, `mmc_blk_remove()`, `mmc_blk_suspend()`, and `mmc_blk_resume()` implement the `struct mmc_driver` lifecycle.
- `mmc_blk_mq_issue_rq()` is the central blk-mq request dispatcher for sync operations, CQE/direct-command operations, and async read/write.
- `mmc_blk_rw_rq_prep()` and `mmc_blk_data_prep()` translate block requests into MMC commands, data descriptors, scatterlists, timeouts, CMD23, reliable write, data tag, and crypto context.
- `mmc_blk_mq_rw_recovery()`, `mmc_blk_reset()`, `mmc_blk_cqe_recovery()`, and completion helpers handle errors, retuning, card busy polling, partial completion, single-block retry, and hardware reset.
- `mmc_blk_ioctl_cmd()` and `mmc_blk_ioctl_multi_cmd()` marshal `MMC_IOC_CMD` and `MMC_IOC_MULTI_CMD` through the block queue.

## Control Flow
Module init registers the RPMB bus, allocates a char-device range, registers the fixed MMC block major, then registers the `mmcblk` driver on the MMC bus. Probe validates read command support, applies quirks, creates a high-priority completion workqueue, allocates the main disk, adds eMMC partitions/RPMB devices, enables debugfs entries, and configures runtime PM. For normal I/O, the queue layer calls `mmc_blk_mq_issue_rq()`, which switches to the target eMMC partition, chooses sync versus async/CQE handling, prepares MMC requests, starts them through the core, and completes or requeues requests based on transferred bytes and errors. Raw ioctls are wrapped as driver-specific block requests so they serialize with normal I/O.

## State And Persistence
Persistent runtime state includes allocated disk minors, gendisk capacity/read-only flags, current eMMC partition cache (`part_curr`), per-request retry flags, reset-done bits, card write tracking, RPMB devices, runtime PM state, and debugfs/sysfs values. Hardware partition selection persists in EXT_CSD until switched back; the driver tracks and restores it during remove/resume/reset. No driver-owned disk files are written, but the whole purpose is access to card media.

## Dependencies And Integration Points
Depends on the MMC bus/core APIs, block layer/blk-mq, queue helper code, eMMC/SD protocol helpers, RPMB framework, debugfs, sysfs, runtime PM, IDA allocation, workqueues, capabilities checks, user-copy helpers, and optional inline crypto. It exports block devices as `mmcblkN`, hardware partitions such as `boot0`/`gp0`, and RPMB char devices/bus entries.

## Risks And Edge Cases
Raw ioctls require `CAP_SYS_RAWIO` on the whole disk to avoid partition overspray, but they can still issue powerful card commands. Partition switching around RPMB disables command queueing and pauses retuning; failure to restore the previous partition can corrupt later I/O. Recovery logic is complex and depends on accurate host status, bytes transferred, and card busy detection. Secure erase/trim timeout calculations must avoid exceeding host busy limits. RPMB frame sizes and reliable-write command sequences are strict. Open/release/kref and disk removal race handling is critical during hot unplug.

## Test Signals
Build `CONFIG_MMC_BLOCK=y/m` with queue support. Runtime signals include creation/removal of `mmcblk*`, read/write/fsstress success, forced read-only sysfs behavior, discard/trim/flush results, ioctl permission tests, RPMB frame routing tests, suspend/resume with partition restoration, CQE and non-CQE I/O, injected CRC/timeouts exercising recovery, and debugfs `status`/`ext_csd` reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/block.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/block.h -->
# sources/distributed-fs/ceph-client/drivers/mmc/core/block.h

## Purpose
Declares the internal interface between the MMC block driver and its queue/blk-mq support code.

## Important APIs, Types, And Functions
- Forward declares `struct mmc_queue`, `struct request`, and `struct work_struct`.
- Declares `mmc_blk_mq_issue_rq()`, `mmc_blk_mq_complete()`, `mmc_blk_mq_recovery()`, and `mmc_blk_mq_complete_work()`.
- Declares `mmc_blk_cqe_recovery()` for command-queue-engine recovery.
- Uses `enum mmc_issued` as the queue dispatch result contract.

## Control Flow
Queue code calls these functions to issue a prepared block request, complete requests from blk-mq callbacks, and run recovery work. `block.c` provides the implementations and keeps policy details out of the queue helper.

## State And Persistence
The header owns no state. It defines function contracts that mutate `struct mmc_queue`, request state, and card/host state in the implementation.

## Dependencies And Integration Points
Integrates `block.c` with `queue.c` and the Linux block request lifecycle. It is private to the MMC core tree rather than a public UAPI.

## Risks And Edge Cases
Prototype drift between `queue.c` and `block.c` would break the build. The incomplete enum forward declaration means callers must include the header that defines `enum mmc_issued` before using values.

## Test Signals
Compile coverage of `mmc_block-objs := block.o queue.o` validates the interface. Runtime queue dispatch and recovery tests indirectly validate these contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/block.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/bus.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/core/bus.c

## Purpose
Implements the MMC card bus type and driver-model integration for `struct mmc_card` devices. It handles card allocation, registration, uevents, sysfs type attributes, driver probe/remove/shutdown, PM callbacks, and card teardown.

## Important APIs, Types, And Functions
- `mmc_bus_type` defines the `mmc` bus with `.uevent`, `.probe`, `.remove`, `.shutdown`, and PM operations.
- `mmc_register_bus()` and `mmc_unregister_bus()` register/unregister the bus.
- `mmc_register_driver()` and `mmc_unregister_driver()` bind `struct mmc_driver` instances to the bus.
- `mmc_alloc_card()` allocates and initializes a card device.
- `mmc_add_card()` names, logs, debugfs-registers, OF-links, and adds a card device.
- `mmc_remove_card()` unregisters, removes debugfs, disables CQE if needed, drops OF references, and releases the device.

## Control Flow
MMC core init registers the bus before host/card discovery. Protocol attach code allocates cards with `mmc_alloc_card()`, fills identity/type fields, and calls `mmc_add_card()`. The driver core emits uevents and probes matching MMC drivers such as `mmcblk`. During removal/shutdown/suspend/resume, bus callbacks delegate to the bound `mmc_driver` and the current host `bus_ops`.

## State And Persistence
State lives in `struct mmc_card` devices registered with the driver model. `MMC_STATE_PRESENT` is set after successful `device_add()` and checked during removal. OF child node references, debugfs roots, runtime PM state, and CQE enabled flags are managed across the card lifetime.

## Dependencies And Integration Points
Depends on Linux driver core, sysfs, PM, OF, MMC host/card definitions, SDIO CIS cleanup, MMC debugfs helpers, and protocol bus operations. It emits uevent variables such as `MMC_TYPE`, `SDIO_ID`, `MMC_NAME`, and `MODALIAS=mmc:block`.

## Risks And Edge Cases
Uevent content drives module autoloading; missing `MODALIAS=mmc:block` would prevent block driver autoload for storage cards. Shutdown calls `__mmc_stop_host()` before optional bus shutdown, so bus ops must tolerate stopped detection. Card removal must balance OF node and device references and disable CQE to avoid later queue activity.

## Test Signals
Boot/probe logs should show correct card type/speed messages. Udev should see expected `MMC_TYPE`, SDIO, and modalias variables. Module autoload of `mmc_block`, suspend/resume callbacks, card insertion/removal, and CQE disable on removal are key runtime signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/bus.h -->
# sources/distributed-fs/ceph-client/drivers/mmc/core/bus.h

## Purpose
Provides private declarations for the MMC bus and media-driver interface.

## Important APIs, Types, And Functions
- `MMC_DEV_ATTR()` creates read-only sysfs attributes backed by `struct mmc_card`.
- `struct mmc_driver` wraps a `struct device_driver` with MMC-card `probe`, `remove`, and `shutdown` callbacks.
- Declares `mmc_alloc_card()`, `mmc_add_card()`, `mmc_remove_card()`, bus register/unregister helpers, and driver register/unregister helpers.

## Control Flow
Protocol attach code uses card allocation/registration helpers. Media drivers define `struct mmc_driver` and register it on the MMC bus. The driver core later invokes callbacks through `bus.c`.

## State And Persistence
The header owns no state; it defines contracts for card devices and drivers that are persisted in the driver model during runtime.

## Dependencies And Integration Points
Depends on `linux/device.h`, `linux/sysfs.h`, and internal `struct mmc_host`/`struct mmc_card` users. It is consumed by core protocol files and block/SDIO-style media drivers.

## Risks And Edge Cases
Because this is a private bus contract, changing callback shapes or attribute macros requires coordinated updates across all MMC media drivers.

## Test Signals
Compile coverage of all MMC core and media drivers validates the header. Runtime probe/remove of `mmcblk` validates the `struct mmc_driver` path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/bus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/card.h -->
# sources/distributed-fs/ceph-client/drivers/mmc/core/card.h

## Purpose
Defines private MMC card helpers: state-bit accessors, card identity helpers, fixup-table structures/macros, vendor IDs, and quirk manipulation functions.

## Important APIs, Types, And Functions
- Card-state bits include present, read-only, block addressing, SDXC, removed, suspended, and SDUC.
- `mmc_card_*` and `mmc_card_set_*` macros read/write state flags.
- `struct mmc_fixup` describes CID/CIS/OF-compatible match criteria and a `vendor_fixup()` callback.
- `MMC_FIXUP*`, `SDIO_FIXUP*`, and `END_FIXUP` macros build fixup tables.
- Inline helpers add/remove quirks globally or only for MMC/SD products, set rate limits, and model known nonstandard devices such as `wl1251`.

## Control Flow
Card identification code fills card fields and then fixup code walks tables built with these macros. Matching entries call vendor fixup callbacks to adjust card quirks, capabilities, or limits before higher-level drivers use the card.

## State And Persistence
State changes are in-memory fields on `struct mmc_card`, especially `state`, `quirks`, `quirk_max_rate`, CIS fields, and SDIO function metadata. These changes persist for the lifetime of the detected card.

## Dependencies And Integration Points
Depends on public `linux/mmc/card.h` and SDIO IDs. It is used by core protocol files, quirk tables, and block code to check card behavior such as CMD23 support restrictions, erase/trim limitations, or nonstandard SDIO setup.

## Risks And Edge Cases
Incorrect fixup matches can disable performance features or enable unsafe commands on unrelated media. CID revision/date matching must handle vendor firmware changes. Quirk helpers are inline and easy to call from broad tables, so table specificity is the main safety boundary.

## Test Signals
Card probe logs and debugfs `quirks` values should match expected fixups for known cards. Regression tests include cards with broken CMD23, trim/secure erase quirks, nonstandard SDIO, and rate-limit quirks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/card.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/core.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/core/core.c

## Purpose
Implements core MMC/SD/SDIO request execution, host claiming, power sequencing, voltage/timing control, erase/discard helpers, card detection/rescan, card removal checks, CQE recovery, and subsystem init/exit.

## Important APIs, Types, And Functions
- Request APIs: `mmc_start_request()`, `mmc_request_done()`, `mmc_wait_for_req()`, `mmc_wait_for_cmd()`, `mmc_cqe_start_req()`, `mmc_cqe_request_done()`, and `mmc_cqe_recovery()`.
- Host ownership APIs: `__mmc_claim_host()`, `mmc_release_host()`, `mmc_get_card()`, and `mmc_put_card()`.
- Bus/power APIs: `mmc_attach_bus()`, `mmc_detach_bus()`, `mmc_power_up()`, `mmc_power_off()`, `mmc_power_cycle()`, and `mmc_set_initial_state()`.
- Signal/timing APIs: `mmc_set_clock()`, `mmc_set_bus_width()`, `mmc_set_timing()`, `mmc_select_voltage()`, and UHS voltage-switch helpers.
- Erase helpers: `mmc_init_erase()`, `mmc_erase()`, `mmc_calc_max_discard()`, and capability predicates.
- Detection APIs: `mmc_detect_change()`, `mmc_rescan()`, `_mmc_detect_card_removed()`, `mmc_start_host()`, and `mmc_stop_host()`.

## Control Flow
Host drivers claim the host and submit requests through core helpers. The core prepares command/data objects, performs retuning if needed, validates scatterlist sizes against host limits, traces request start/done, and delegates actual transfer to host `ops->request()` or CQE ops. Completion handles retries, CRC-triggered retuning, fault injection, LEDs, and done callbacks. Separately, rescan work powers up the bus, tries UHS-II, then SDIO, SD, and MMC attachment at descending initialization frequencies. Stop/removal cancels detect work, invokes bus removal, detaches bus ops, and powers off.

## State And Persistence
Key runtime state lives in `struct mmc_host`: claimed/claimer counts, current `ios`, retune flags/timer, ongoing request, detect work, bus ops, card pointer, PM state, error stats, and power sequencing state. Card erase geometry, preferred discard sizes, and removal flags are updated during identification and runtime. No disk state is stored by this file.

## Dependencies And Integration Points
Depends on host controller callbacks, CQE callbacks, power sequencing, GPIO card detect, regulator/undervoltage hooks, runtime PM, workqueues, completions, tracepoints, LED triggers, fault injection, SD/SDIO/MMC protocol helpers, and optional crypto reset hooks.

## Risks And Edge Cases
Host claiming is a global serialization point; mismatched claim/release or nested contexts can deadlock. Retuning must be held across sensitive requests and CQE recovery. Voltage switching can require power cycling after partial failure. Erase/discard timeout math must avoid overflow and respect host busy limits. Card removal can race with in-flight requests and slow mechanical detect switches. Fault injection can create partial transfers that upper layers must handle.

## Test Signals
Signals include successful card enumeration across SDIO/SD/MMC, tracepoints for request start/done, request retry behavior on injected failures, CQE recovery under command queue errors, suspend/resume and runtime PM stability, discard/trim correctness, voltage-switch fallbacks, and clean hotplug removal without use-after-free or stuck detect work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/core.h -->
# sources/distributed-fs/ceph-client/drivers/mmc/core/core.h

## Purpose
Declares the private MMC core API shared across protocol, bus, block, host, and helper files.

## Important APIs, Types, And Functions
- `struct mmc_bus_ops` defines active bus callbacks for remove, detect, suspend/resume, alive checks, reset, cache handling, and undervoltage handling.
- Declares power, voltage, timing, request, erase, host claim, detection, bus attach, and card attach helpers.
- Provides inline `mmc_delay()`, `mmc_claim_host()`, `mmc_pre_req()`, `mmc_post_req()`, `mmc_cache_enabled()`, `mmc_flush_cache()`, and sector division/modulo helpers.
- Includes conditional debugfs declarations or no-op stubs based on `CONFIG_DEBUG_FS`.

## Control Flow
Implementation files include this header to call into core request/power/detection helpers and to attach protocol-specific bus operations to a host. Host drivers and block paths use the declared functions to serialize access and submit commands.

## State And Persistence
The header owns no state. It defines how `struct mmc_host`, `struct mmc_card`, and `struct mmc_request` state is accessed and mutated by the core implementation.

## Dependencies And Integration Points
Depends on Linux delay/scheduler primitives and public MMC host/card/request structures. It is a central private integration contract for `core.c`, protocol attach files, `block.c`, `bus.c`, `host.c`, debugfs, and power helpers.

## Risks And Edge Cases
Because many files depend on this header, signature or semantic changes have broad blast radius. Inline cache and pre/post request wrappers assume `host->bus_ops` and `host->ops` are valid for the current lifecycle phase.

## Test Signals
Compile all MMC core configurations to catch prototype drift. Runtime smoke tests for card attach, request submission, erase/discard, debugfs no-op behavior, and suspend/resume validate the declared contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/crypto.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/core/crypto.c

## Purpose
Adds MMC inline encryption glue between block-layer crypto and MMC requests for hosts advertising crypto capability.

## Important APIs, Types, And Functions
- `mmc_crypto_set_initial_state()` reprograms all block-crypto keys after resets that may clear hardware keyslots.
- `mmc_crypto_setup_queue()` registers the host crypto profile with a request queue.
- `mmc_crypto_prepare_req()` copies a block request's crypto context and keyslot index into the outgoing `struct mmc_request`.

## Control Flow
Host/queue initialization calls `mmc_crypto_setup_queue()` when crypto support is enabled. Power reset/initial-state paths call `mmc_crypto_set_initial_state()`. Before block data requests are issued, `mmc_blk_data_prep()` calls `mmc_crypto_prepare_req()` so host drivers can program/use the selected crypto context.

## State And Persistence
The file does not own key material. It references `host->crypto_profile`, request crypto contexts, and block crypto keyslots. Keyslot programming persists in host hardware until reset or reprogramming.

## Dependencies And Integration Points
Depends on `CONFIG_MMC_CRYPTO`, `linux/blk-crypto.h`, public MMC host definitions, and MMC queue/request structures. It integrates with block inline encryption and host controllers that set `MMC_CAP2_CRYPTO`.

## Risks And Edge Cases
If a reset clears hardware keys and reprogramming is skipped, encrypted I/O can fail or use invalid keyslots. Requests without `crypt_ctx` must pass through unchanged. Host capability bits must be accurate so non-crypto hosts are not registered with blk-crypto.

## Test Signals
Build with `CONFIG_MMC_CRYPTO` and `BLK_INLINE_ENCRYPTION`. Runtime signals include blk-crypto queue registration, encrypted I/O success across resets/resume, correct keyslot indices in host traces, and no behavior change for unencrypted requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/crypto.h -->
# sources/distributed-fs/ceph-client/drivers/mmc/core/crypto.h

## Purpose
Declares MMC inline encryption helpers and provides no-op stubs when crypto support is disabled.

## Important APIs, Types, And Functions
- Declares `mmc_crypto_set_initial_state()`, `mmc_crypto_setup_queue()`, and `mmc_crypto_prepare_req()` under `CONFIG_MMC_CRYPTO`.
- Provides static inline empty implementations when `CONFIG_MMC_CRYPTO` is not selected.

## Control Flow
Core and block paths can call crypto helpers unconditionally; the preprocessor selects real implementations or no-ops.

## State And Persistence
The header owns no state. It controls whether crypto state in hosts and requests is touched by compiled code.

## Dependencies And Integration Points
Forward declares MMC host, queue request, and request queue structures. It integrates `core.c`, `block.c`, and queue setup with optional `crypto.c`.

## Risks And Edge Cases
No-op stubs must preserve behavior for non-crypto builds. Prototype drift against `crypto.c` would break `CONFIG_MMC_CRYPTO=y` builds.

## Test Signals
Compile with `CONFIG_MMC_CRYPTO=y` and `n`. Encrypted I/O tests validate the real path; ordinary block I/O tests validate the no-op path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/crypto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/core/debugfs.c

## Purpose
Creates debugfs visibility and control nodes for MMC hosts and cards, including IOS state, capabilities, clock control, error statistics, fault injection, card state, and quirks.

## Important APIs, Types, And Functions
- `mmc_ios_show()` reports clock, voltage, bus mode, chip select, power mode, width, timing, signal voltage, and driver type.
- `mmc_clock_opt_get/set()` reads or changes the host clock while claiming the host.
- `mmc_err_state_get()`, `mmc_err_stats_show()`, and `mmc_err_stats_write()` expose and reset host error counters.
- `mmc_caps_set()` and `mmc_caps2_set()` allow only selected capability bits to be toggled.
- `mmc_add_host_debugfs()` and `mmc_remove_host_debugfs()` manage per-host debugfs trees.
- `mmc_add_card_debugfs()` and `mmc_remove_card_debugfs()` manage per-card state/quirk files.

## Control Flow
When a host is added, the core creates a debugfs directory named after the host and populates control/status files. Card registration adds a child directory for the card ID. Reads format current state; writes to `clock`, `caps`, `caps2`, and `err_stats` mutate controlled host fields. With `CONFIG_FAIL_MMC_REQUEST`, a fault-injection attribute is attached to the host.

## State And Persistence
Debugfs reflects live host/card fields. Error stats persist in memory until reset by writing `err_stats` or reinitializing the host. Capability and clock writes mutate runtime host state but are not stored across reboot.

## Dependencies And Integration Points
Depends on debugfs, seq_file, fault injection, MMC host/card definitions, host claiming, and core clock-setting helpers. It is compiled into `mmc_core` only with `CONFIG_DEBUG_FS`.

## Risks And Edge Cases
Debugfs is a privileged diagnostic surface that can change clocks and capability bits, possibly destabilizing active hardware. Capability setters restrict changes to a whitelist, but changing them at runtime can still diverge from actual controller wiring. Fault injection intentionally corrupts request outcomes for testing.

## Test Signals
With debugfs enabled, host directories should appear under `/sys/kernel/debug/mmc*` naming. Reads of `ios`, `err_stats`, card `state`, and `quirks` should succeed. Clock writes within `f_min..f_max` should update IOS; out-of-range writes should fail. Fault injection should produce request errors and increment stats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/host.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/core/host.c

## Purpose
Implements MMC host class-device allocation, registration, removal, OF/property parsing, retuning management, wakeup resources, debugfs integration, and host capability validation.

## Important APIs, Types, And Functions
- `mmc_register_host_class()` and `mmc_unregister_host_class()` manage the `mmc_host` class.
- Retuning APIs include `mmc_retune_enable()`, pause/unpause, disable, hold/release, timer handling, and `mmc_retune()`.
- `mmc_of_parse()` translates firmware properties into host capabilities, GPIO card-detect/write-protect setup, power-management caps, DSR, delays, and pwrseq allocation.
- `mmc_of_parse_voltage()` converts `voltage-ranges` into OCR masks.
- `mmc_alloc_host()`, `devm_mmc_alloc_host()`, `mmc_add_host()`, `mmc_remove_host()`, and `mmc_free_host()` implement the host lifecycle.
- `mmc_validate_host_caps()` drops unsupported modes such as UHS/HS200 on 1-bit buses or HS400 without 8-bit support.

## Control Flow
Host controller drivers allocate a host, fill operations and capabilities, optionally parse firmware properties, then call `mmc_add_host()`. The core validates capabilities, adds the class device, registers an LED trigger, creates debugfs, and starts card detection. Removal stops detection/card activity, removes debugfs and the class device, and unregisters the LED trigger. Freeing cancels detect work, releases pwrseq, and drops the device reference.

## State And Persistence
Runtime state includes host index allocation, class device lifetime, wakeup source, retune timer/flags, detect work, GPIO descriptors, pwrseq handle, capability masks, IOS defaults, and error/work structures. Firmware-derived settings persist for the host lifetime.

## Dependencies And Integration Points
Depends on driver core classes, IDA, OF/fwnode properties, GPIO slot helpers, pwrseq, SDIO IRQ work, LED triggers, wakeup sources, debugfs helpers, and public MMC host/card APIs.

## Risks And Edge Cases
Retuning state must be balanced across pause/hold/release users or transfers may run without needed tuning. Firmware property parsing can silently drop capabilities when bus width is insufficient, affecting performance. Host index allocation combines OF aliases and IDA allocation; alias mistakes change device names (`mmcN`). Debugfs and detect work must be torn down before freeing host memory.

## Test Signals
Host controller probe should create `/sys/class/mmc_host/mmcN`, debugfs host nodes, LED triggers, and card detection work. Device-tree parsing tests should cover bus widths, voltage ranges, GPIO CD/WP, non-removable, HS200/HS400, power caps, and pwrseq. Retune tests should exercise CRC-triggered retune, timer retune, HS400 transitions, and pause/unpause around RPMB.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/host.h -->
# sources/distributed-fs/ceph-client/drivers/mmc/core/host.h

## Purpose
Provides private host-management declarations and small capability/timing helpers for MMC core users.

## Important APIs, Types, And Functions
- Declares host class registration and all retuning helper functions.
- Inline helpers clear, hold, and recheck retune state.
- Capability predicates include `mmc_host_can_cmd23()`, `mmc_host_can_done_complete()`, `mmc_host_can_access_boot()`, and `mmc_host_can_uhs()`.
- Card timing predicates include HS200, DDR52, HS400, HS400 enhanced strobe, and SD Express checks.

## Control Flow
Core, block, and protocol files include this header to decide whether host/card features are available and to manage retuning around operations.

## State And Persistence
The header owns no state. Inline helpers mutate retune flags/counters in `struct mmc_host` and read host/card IOS/capability fields.

## Dependencies And Integration Points
Depends on public `linux/mmc/host.h`. It is a private integration point between host lifecycle code, request handling, protocol mode switching, and block recovery paths.

## Risks And Edge Cases
Inline retune helpers directly manipulate counters and flags, so misuse can unbalance retune holds. Timing predicates read current IOS state, which can change during mode switches and reset paths.

## Test Signals
Build coverage catches prototype drift. Runtime signals include correct CMD23 selection, done-complete behavior, boot partition access policy, UHS/HS timing decisions, and balanced retune state after error recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/host.h -->
