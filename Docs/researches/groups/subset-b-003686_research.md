<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramnv50.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramnv50.c

## Purpose
Implements NV50-family framebuffer RAM discovery and memory reclocking support. It builds a hardware sequencer program that safely changes memory timings, mode registers, GPIO-controlled voltage/ODT signals, and the memory PLL while FIFO and framebuffer access are quiesced.

## Important APIs, Types, And Functions
Defines `struct nv50_ramseq` as a register-backed `hwsq` script with timing, mode-register, GPIO, PLL, FIFO, and FB-control registers. `struct nv50_ram` embeds `struct nvkm_ram`. Key functions are `nv50_ram_timing_calc`, `nv50_ram_timing_read`, `nv50_ram_calc`, `nv50_ram_prog`, `nv50_ram_tidy`, `nv50_fb_vram_rblock`, `nv50_ram_ctor`, and `nv50_ram_new`.

## Control Flow
`nv50_ram_new` allocates RAM state, calls `nv50_ram_ctor`, and initializes all sequencer register descriptors. `nv50_ram_ctor` reads memory type, size, partitions, ranks, and initializes the VRAM allocator with a row-block size derived from memory-controller registers. For reclocking, `nv50_ram_calc` selects a BIOS performance entry, resolves RAM map and timing data, computes mode registers, emits a sequencer program that waits for vblank, blocks FIFO, disables FB, enters self-refresh, programs MPLL and memory timings, toggles GPIO voltage/ODT lines, resets DLL when required, and re-enables FB/FIFO. `nv50_ram_prog` executes the script when `NvMemExec` allows it; `nv50_ram_tidy` discards it.

## State And Persistence
Persistent driver state includes `ram->base.target`, `ram->base.next`, mode registers, VRAM allocator geometry, partition mask, rank count, and the prepared `hwsq` script. Hardware state is volatile MMIO state in memory controller, PLL, GPIO, and FIFO/FB registers. BIOS tables are read-only inputs.

## Dependencies And Integration Points
Depends on Nouveau BIOS parsers for performance, PLL, RAM map, RAM config, and timing records; on GPIO DCB lookup for memory-control pins; on PLL calculation; on `hwsq` sequencing helpers; and on shared RAM helpers such as `nvkm_gddr3_calc`. It integrates with the framebuffer subdev through `nvkm_ram_func`.

## Risks And Edge Cases
The code has chipset-specific and poorly documented bit handling, with several `XXX` comments. Missing or malformed VBIOS tables fail reclocking. Timing support is narrow, mode register calculation is implemented for GDDR3 in this path, and an incorrect sequencer can hang display or memory access. VRAM geometry mismatches are warned about but not fatal.

## Test Signals
Useful signals are successful boot-time VRAM sizing, no VBIOS parsing errors, debug logs for timing registers and row-block size, successful memory reclock without FIFO/FB hangs, and suspend/resume or mode-setting stability under memory pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramnv50.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramseq.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramseq.h

## Purpose
Provides small framebuffer-RAM-specific wrappers around the generic hardware sequencer API.

## Important APIs, Types, And Functions
Macros include `ram_init`, `ram_exec`, `ram_have`, `ram_rd32`, `ram_wr32`, `ram_nuke`, `ram_mask`, `ram_setf`, `ram_wait`, `ram_wait_vblank`, and `ram_nsec`. They assume the caller has a sequencer struct with `base` and `r_<name>` register members.

## Control Flow
The macros compile register names such as `0x100200` or `mr[0]` into `r_<name>` accesses and forward them to `hwsq_*`. They are used while constructing a deferred script and later executing or discarding it.

## State And Persistence
No independent state is stored here. State lives in the caller-owned `hwsq` object and its register descriptors.

## Dependencies And Integration Points
Depends on the hardware sequencer interface and is included by RAM-reclocking implementations such as `ramnv50.c`.

## Risks And Edge Cases
Because these are macros, invalid register names fail at compile time or map to the wrong field if the caller's struct is inconsistent. There is no runtime validation beyond the underlying `hwsq` helpers.

## Test Signals
Successful compilation of RAM reclocking code and correct sequencer execution are the main signals. Register-level debug logs from callers help confirm macro-generated operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/ramseq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/regsnv04.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/regsnv04.h

## Purpose
Defines legacy NV04 framebuffer register addresses and selected bitfields used by older framebuffer code.

## Important APIs, Types, And Functions
Exports constants for `NV04_PFB_BOOT_0`, memory type/amount fields, RAM width, and `NV04_PFB_CFG0`. There are no functions or data objects.

## Control Flow
This header has no runtime flow. Including code uses the symbolic constants when reading or masking MMIO registers.

## State And Persistence
No driver state is stored. The constants describe persistent hardware register ABI.

## Dependencies And Integration Points
Integrates with early Nouveau framebuffer implementations and any code that decodes NV04-class PFB boot/configuration registers.

## Risks And Edge Cases
Incorrect masks or shifts would misdecode memory type, width, or amount on old GPUs. This file does not validate chipset applicability.

## Test Signals
Boot logs and VRAM sizing on NV04-era hardware are the relevant signals, together with compiler checks for include users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/regsnv04.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/sddr2.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/sddr2.c

## Purpose
Calculates SDR DDR2 mode register values from Nouveau RAM timing and configuration data.

## Important APIs, Types, And Functions
Defines `struct ramxlat`, `ramxlat`, translation tables for DDR2 CAS latency and write recovery encodings, and exported `nvkm_sddr2_calc(struct nvkm_ram *ram)`.

## Control Flow
`nvkm_sddr2_calc` reads timing version 0x10 or 0x20 data, derives CL, WR, DLL state, and ODT state, falls back to existing MR1 ODT bits when timing data is unavailable or version 0x20 is used, translates timing values to register encodings, then updates `ram->mr[0]` and `ram->mr[1]`.

## State And Persistence
It mutates only the pending mode-register array on `struct nvkm_ram`; hardware is not written directly. The caller later programs these values through the RAM sequencer.

## Dependencies And Integration Points
Depends on `struct nvkm_ram` BIOS timing fields and is consumed by memory reclocking paths that support DDR2.

## Risks And Edge Cases
Unsupported timing versions return `-ENOSYS`; unsupported CL/WR values return `-EINVAL`. Some DDR2 encodings are noted as only present in some documentation, so VBIOS entries outside the tables will fail.

## Test Signals
Passing reclock calculations, correct MR values in debug traces, and stable DDR2 reclocking are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/sddr2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/sddr3.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/sddr3.c

## Purpose
Calculates SDR DDR3 mode-register values from BIOS timing data and existing mode register state.

## Important APIs, Types, And Functions
Defines `struct ramxlat`, translation helper `ramxlat`, tables for DDR3 CL, WR, and CWL encodings, and exported `nvkm_sddr3_calc`.

## Control Flow
The function reads timing version 0x10 or 0x20. Version 0x10 requires a header large enough to include CWL; otherwise it returns `-ENOSYS`. Version 0x20 decodes CL/CWL/WR from packed timing words and derives ODT from existing MR1 bits. It translates all values, updates MR0, MR1, and MR2, and leaves actual programming to callers.

## State And Persistence
Only `ram->mr[]` is changed. BIOS timing fields and current MR values are inputs.

## Dependencies And Integration Points
Used by RAM reclocking code through the shared Nouveau RAM layer. It depends on BIOS timing decoding and the caller's earlier capture of current mode registers.

## Risks And Edge Cases
Unsupported timing values or missing CWL data cause explicit errors. The version 0x20 ODT path is marked as a placeholder that should eventually come from VBIOS.

## Test Signals
Expected signals are successful MR calculation, no `-EINVAL` or `-ENOSYS` during reclocking, and stable DDR3 mode after memory frequency changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/sddr3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/tu102.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/tu102.c

## Purpose
Defines the TU102-class framebuffer subdevice implementation and firmware declarations for VPR scrubber support.

## Important APIs, Types, And Functions
Exports `tu102_fb_vpr_scrub_required` and `tu102_fb_new`. Provides `tu102_fb` as an `nvkm_fb_func` table using GF100/GM200/GP100/GP102/GV100 helpers for construction, oneinit, init, page init, vidmem sizing, VPR scrub, RAM creation, and big-page defaults.

## Control Flow
`tu102_fb_new` delegates to `gp102_fb_new_` with the TU102 function table. `tu102_fb_vpr_scrub_required` returns true when register `0x100cd0` has the low bit set, causing the shared framebuffer path to request VPR scrub. Firmware names for TU102/TU104/TU106/TU116/TU117 scrubbers are declared for module firmware loading.

## State And Persistence
No custom persistent state is added beyond the inherited framebuffer object. It observes VPR hardware state and relies on firmware blobs.

## Dependencies And Integration Points
Integrates with framebuffer core, GP102 RAM setup, GV100 page init, and NVDEC scrubber firmware.

## Risks And Edge Cases
Missing scrubber firmware or incorrect VPR status detection can break protected-memory cleanup. The implementation is mostly a table composition, so errors are usually from incompatible inherited helpers.

## Test Signals
Successful framebuffer initialization on Turing GPUs, correct VRAM size, successful VPR scrub when required, and absence of firmware load errors are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/tu102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fsp/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fsp/Kbuild

## Purpose
Builds the FSP subdevice objects into the Nouveau NVKM module.

## Important APIs, Types, And Functions
Lists `base.o`, `gh100.o`, `gb100.o`, and `gb202.o` in `nvkm-y`.

## Control Flow
Kbuild includes these objects unconditionally in the NVKM build when this source tree is built.

## State And Persistence
No runtime state. It controls build composition.

## Dependencies And Integration Points
Connects FSP base logic with GH100 and Blackwell generation implementations.

## Risks And Edge Cases
Omitting a generation object would leave its constructor unresolved or unsupported. Adding an object without matching declarations can create link errors.

## Test Signals
Kernel module build success and availability of FSP constructors for supported GPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fsp/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fsp/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fsp/base.c

## Purpose
Provides the common Firmware Security Processor subdevice wrapper used to wait for secure boot and boot authenticated GSP-FMC images.

## Important APIs, Types, And Functions
Exports `nvkm_fsp_boot_gsp_fmc`, `nvkm_fsp_verify_gsp_fmc`, and `nvkm_fsp_new_`. Defines subdev lifecycle callbacks `nvkm_fsp_preinit` and `nvkm_fsp_dtor`, plus the FSP Falcon configuration using `gp102_flcn_emem_pio`.

## Control Flow
Construction stores the generation `nvkm_fsp_func`, initializes the NVKM subdev, and constructs a Falcon at base `0x8f2000`. Preinit calls the generation `wait_secure_boot` hook. GSP-FMC boot and certificate-size verification are forwarded through `fsp->func->cot`.

## State And Persistence
Persistent state is the `struct nvkm_fsp`, its function table, subdev object, and Falcon object. Hardware state lives in the FSP Falcon and its queues.

## Dependencies And Integration Points
Used by GH100/GB100/GB202 FSP constructors and by GSP initialization code that calls `nvkm_fsp_boot_gsp_fmc`.

## Risks And Edge Cases
The base layer assumes non-null function hooks for secure-boot wait and COT boot. Size mismatches prevent booting authenticated firmware.

## Test Signals
Successful FSP preinit, successful GSP-FMC boot handoff, and no Falcon constructor or secure-boot timeout failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fsp/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fsp/gb100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fsp/gb100.c

## Purpose
Defines GB100-family FSP function data for Blackwell GB10x GSP-FMC secure boot.

## Important APIs, Types, And Functions
Provides `gb100_fsp` with GH100 queue/wait/boot hooks, COT version 2, and certificate component sizes of 48-byte hash, 97-byte public key, and 96-byte signature. Exports `gb100_fsp_new`.

## Control Flow
The constructor simply delegates to `nvkm_fsp_new_` with this function table. Runtime boot flow is inherited from GH100 helpers through the table.

## State And Persistence
No additional state beyond the base FSP object and generation constants.

## Dependencies And Integration Points
Integrates GB100 GSP code with the shared FSP COT boot path and `gh100_fsp_wait_secure_boot`/`gh100_fsp_boot_gsp_fmc`.

## Risks And Edge Cases
Incorrect COT version or key/signature sizes will make `nvkm_fsp_verify_gsp_fmc` reject firmware or make FSP reject the boot command.

## Test Signals
Successful GB100 FSP construction, COT image verification, and GSP-FMC boot through FSP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fsp/gb100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fsp/gb202.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fsp/gb202.c

## Purpose
Defines GB202/GB20x FSP function data for Blackwell GSP-FMC secure boot.

## Important APIs, Types, And Functions
Provides a `gb202_fsp` function table reusing GH100 secure-boot wait and COT boot functions, with Blackwell COT version and key/signature sizes. Exports `gb202_fsp_new`.

## Control Flow
Construction delegates to `nvkm_fsp_new_`; later preinit and boot are handled via the function pointers populated here.

## State And Persistence
No custom runtime state is added. The critical persistent information is the generation-specific COT metadata in the function table.

## Dependencies And Integration Points
Used by GB202-class GSP initialization. It relies on the same FSP MCTP/NVDM command exchange as GH100.

## Risks And Edge Cases
The secure boot path is sensitive to COT sizes and version. A mismatch with firmware packaging or FSP ROM expectations causes early GSP boot failure.

## Test Signals
Successful firmware size verification, no FSP command failure, and completed GSP-FMC boot on GB20x devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fsp/gb202.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fsp/gh100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fsp/gh100.c

## Purpose
Implements GH100 FSP queue protocol and COT command used to authenticate and start GSP-FMC.

## Important APIs, Types, And Functions
Defines packed MCTP/NVDM payload structures, `gh100_fsp_poll`, `gh100_fsp_recv`, `gh100_fsp_wait`, `gh100_fsp_send`, `gh100_fsp_send_sync`, `gh100_fsp_boot_gsp_fmc`, `gh100_fsp_wait_secure_boot`, `gh100_fsp_new`, and `gh100_fsp` function metadata.

## Control Flow
The send path waits for the outbound FSP queue to empty, writes a DWORD-aligned packet to Falcon EMEM, and updates queue pointers. The sync path waits for an inbound response, reads it from EMEM, resets message queue pointers, validates MCTP and NVDM headers, checks the echoed command type, and maps nonzero FSP error codes to `-EIO`. The COT boot function builds an NVDM COT message containing FMC image address, optional FRTS vidmem placement, hash, public key, signature, and boot args address. Secure-boot wait polls a thermal scratch field for FSP boot success.

## State And Persistence
State is primarily hardware queue pointers, Falcon EMEM contents, and the FSP boot status scratch register. Function table constants persist in the driver object.

## Dependencies And Integration Points
Depends on GH100 hardware register definitions, Falcon EMEM PIO helpers, DRM field macros, and the base FSP subdevice. Called by GH100/Blackwell GSP init through `nvkm_fsp_boot_gsp_fmc`.

## Risks And Edge Cases
Packet sizes must be DWORD aligned and fit the receive buffer. Queue timeouts, unexpected headers, command mismatches, or FSP error codes abort boot. Resume changes FRTS handling.

## Test Signals
Secure-boot wait success, successful COT response, no timeout in queue send/wait, and later GSP lockdown release are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fsp/gh100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fsp/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fsp/priv.h

## Purpose
Declares private FSP subdevice types and generation hooks.

## Important APIs, Types, And Functions
Defines `nvkm_fsp(p)` and `struct nvkm_fsp_func`, including `wait_secure_boot` and nested `cot` metadata and `boot_gsp_fmc` hook. Declares `nvkm_fsp_new_`, `gh100_fsp_wait_secure_boot`, and `gh100_fsp_boot_gsp_fmc`.

## Control Flow
No runtime flow. It provides the function-table contract consumed by FSP base and generation files.

## State And Persistence
The function table persists in each `struct nvkm_fsp`; certificate sizes and COT version are immutable generation metadata.

## Dependencies And Integration Points
Includes public `subdev/fsp.h` and bridges base code, GH100 implementation, and Blackwell wrappers.

## Risks And Edge Cases
Function pointer contracts are not enforced at compile time beyond type checks; missing hooks can crash through null calls in base code.

## Test Signals
Successful compilation and correct constructor wiring for each generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fsp/priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fuse/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fuse/Kbuild

## Purpose
Builds the fuse subdevice implementations.

## Important APIs, Types, And Functions
Adds `base.o`, `nv50.o`, `gf100.o`, and `gm107.o` to `nvkm-y`.

## Control Flow
Kbuild compiles the common fuse layer and generation-specific readers into NVKM.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Connects the public fuse subsystem with NV50, GF100, and GM107 reader implementations.

## Risks And Edge Cases
Missing objects break constructor availability or link coverage for supported chipsets.

## Test Signals
Build success and successful fuse subdevice construction on supported hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fuse/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fuse/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fuse/base.c

## Purpose
Provides the common NVKM fuse subdevice wrapper and dispatches fuse reads to generation-specific register accessors.

## Important APIs, Types, And Functions
Exports `nvkm_fuse_read` and `nvkm_fuse_new_`. Defines the subdev destructor and initializes a spinlock in each `struct nvkm_fuse`.

## Control Flow
Construction allocates the fuse object, initializes the NVKM subdev, stores the function table, and initializes the lock. `nvkm_fuse_read` calls `fuse->func->read`.

## State And Persistence
Persistent state is the fuse subdev object, function table, and spinlock. Fuses themselves are hardware-programmed nonvolatile state, but this file only reads through lower layers.

## Dependencies And Integration Points
Used by chipset-specific files and public fuse consumers that need strap, security, or configuration data.

## Risks And Edge Cases
No validation exists for missing `read` hooks. The lock only protects readers that use it; generation code must correctly preserve gate registers.

## Test Signals
Successful fuse reads and absence of register-gating races under concurrent calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fuse/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fuse/gf100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fuse/gf100.c

## Purpose
Implements GF100-class fuse reads with required register gating.

## Important APIs, Types, And Functions
Defines `gf100_fuse_read`, `gf100_fuse` function table, and `gf100_fuse_new`.

## Control Flow
The read path takes the fuse spinlock, enables fuse access through `0x022400`, sets an auxiliary bit at `0x021000`, reads from `0x021100 + addr`, restores both modified registers, and releases the lock.

## State And Persistence
It temporarily changes hardware gate registers and restores them. No software state persists beyond the shared fuse object.

## Dependencies And Integration Points
Uses `nvkm_mask`, `nvkm_rd32`, `nvkm_wr32`, and common `nvkm_fuse_new_`.

## Risks And Edge Cases
Comments note potential races if other NVKM code writes the same registers. Locking only coordinates users of this fuse object.

## Test Signals
Correct fuse values, no stale gate state after reads, and no race symptoms during concurrent initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fuse/gf100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fuse/gm107.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fuse/gm107.c

## Purpose
Implements GM107-class direct fuse reads, with GSP-RM exclusion.

## Important APIs, Types, And Functions
Defines `gm107_fuse_read`, `gm107_fuse`, and `gm107_fuse_new`.

## Control Flow
Reads directly from `0x021100 + addr`. Constructor returns `-ENODEV` when `nvkm_gsp_rm(device->gsp)` is active, preventing a duplicate local fuse subdevice when RM owns fuse-like services.

## State And Persistence
No software state beyond the common fuse object. Hardware fuses are read-only persistent state.

## Dependencies And Integration Points
Depends on public GSP helper `nvkm_gsp_rm` and common fuse construction.

## Risks And Edge Cases
Under GSP-RM, callers must not expect this local fuse subdevice to exist. Direct reads assume access is already available on this generation.

## Test Signals
Successful constructor on non-GSP-RM GM107 paths, `-ENODEV` with GSP-RM, and correct fuse values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fuse/gm107.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fuse/nv50.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fuse/nv50.c

## Purpose
Implements NV50-class fuse reads with access enable preservation.

## Important APIs, Types, And Functions
Defines `nv50_fuse_read`, `nv50_fuse`, and `nv50_fuse_new`.

## Control Flow
The read path takes the fuse lock, sets bit `0x800` in register `0x001084`, reads from `0x021000 + addr`, restores the original enable register value, and releases the lock.

## State And Persistence
The only transient state is the enable register bit. Persistent state remains in hardware fuses and the common fuse object.

## Dependencies And Integration Points
Uses common fuse construction and MMIO helpers. Consumers call through `nvkm_fuse_read`.

## Risks And Edge Cases
The code notes possible races with other code touching the enable register. Address validation is left to callers and hardware behavior.

## Test Signals
Correct reads on NV50-era devices and no residual change to `0x001084` after reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fuse/nv50.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fuse/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fuse/priv.h

## Purpose
Declares the private fuse subdevice function-table contract.

## Important APIs, Types, And Functions
Defines `nvkm_fuse(p)`, `struct nvkm_fuse_func` with `read`, and `nvkm_fuse_new_`.

## Control Flow
No runtime control flow. Generation files include it to provide constructors and read hooks.

## State And Persistence
No state is stored in the header. The function pointer persists in constructed fuse objects.

## Dependencies And Integration Points
Includes public `subdev/fuse.h` and is used by base and generation implementations.

## Risks And Edge Cases
The interface exposes only a raw `u32 addr` read hook; policy and address validation are external.

## Test Signals
Compile/link correctness and successful dispatch from `nvkm_fuse_read`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fuse/priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gpio/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gpio/Kbuild

## Purpose
Builds Nouveau GPIO subdevice support for multiple GPU generations.

## Important APIs, Types, And Functions
Adds common `base.o` and generation objects `nv10.o`, `nv50.o`, `g94.o`, `gf119.o`, `gk104.o`, and `ga102.o`.

## Control Flow
Kbuild includes these objects in the NVKM build.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Connects shared GPIO APIs with chipset register-map implementations.

## Risks And Edge Cases
Missing an object removes constructor support for a generation. Adding new GPIO generations requires corresponding build inclusion.

## Test Signals
Build success and constructor availability for all listed generations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gpio/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gpio/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gpio/base.c

## Purpose
Implements the common GPIO subdevice: BIOS lookup, set/get helpers, interrupt event dispatch, initialization power checks, and teardown.

## Important APIs, Types, And Functions
Exports `nvkm_gpio_reset`, `nvkm_gpio_find`, `nvkm_gpio_set`, `nvkm_gpio_get`, and `nvkm_gpio_new_`. Defines event callbacks `nvkm_gpio_intr_init/fini`, ISR `nvkm_gpio_intr`, lifecycle `nvkm_gpio_init/fini/dtor`, Apple reset DMI quirk, and external-power GPIO checks.

## Control Flow
Callers locate GPIO lines by tag/line via DCB BIOS records or an Apple TV GPIO quirk. Set/get map logical states through BIOS `log[]` bits and call generation `drive`/`sense`. Interrupt subscription masks line/type pairs; the subdev ISR reads hi/lo status and notifies `nvkm_event`. Init optionally resets GPIOs on selected Apple hardware and checks external power warning GPIOs unless `NvPowerChecks=0`.

## State And Persistence
Stores `struct nvkm_gpio`, function table, and event object. It changes hardware interrupt masks and GPIO output direction/state through generation hooks.

## Dependencies And Integration Points
Depends on BIOS DCB GPIO parsers, DMI, NVKM events, config options, and generation function tables. Used by display, memory reclocking, thermal, and power-management paths.

## Risks And Edge Cases
Wrong BIOS GPIO metadata can invert or drive pins incorrectly. Power checks can block driver init if GPIOs report missing power. Interrupt masks must be cleared on fini to prevent stale notifications.

## Test Signals
Successful GPIO lookup/set/get, hotplug or GPIO event delivery, absence of false power-cable errors, and clean interrupt masking during shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gpio/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gpio/g94.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gpio/g94.c

## Purpose
Adds G94-class 32-line GPIO interrupt handling while reusing NV50 drive/sense/reset behavior.

## Important APIs, Types, And Functions
Exports `g94_gpio_intr_stat`, `g94_gpio_intr_mask`, and `g94_gpio_new`. Defines `g94_gpio` with 32 lines.

## Control Flow
Interrupt status reads two register pairs (`0x00e050/54` and `0x00e070/74`), combines lower and upper 16-bit banks into hi/lo masks, and acknowledges both interrupt registers. Masking updates both banks according to requested hi/lo types.

## State And Persistence
State is hardware interrupt enable/status bits. The software object is created by `nvkm_gpio_new_`.

## Dependencies And Integration Points
Reuses `nv50_gpio_drive`, `nv50_gpio_sense`, and `nv50_gpio_reset`; integrates with common GPIO event dispatch.

## Risks And Edge Cases
Bit packing across two 16-line banks must remain correct. Mis-acknowledging interrupts can lose or repeat notifications.

## Test Signals
Correct events on GPIO lines 0-31 and no interrupt storm after acknowledge.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gpio/g94.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gpio/ga102.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gpio/ga102.c

## Purpose
Implements GA102-class GPIO registration with Ampere register/reset behavior and GSP-RM exclusion.

## Important APIs, Types, And Functions
Defines GA102 GPIO reset and function table, and exports `ga102_gpio_new`. It uses GF119-style drive/sense or compatible helpers while adapting reset registers for GA102.

## Control Flow
Reset walks BIOS GPIO entries, applies default logical states through common `nvkm_gpio_set`, and programs generation-specific pin configuration. Constructor declines local GPIO creation when GSP-RM is active.

## State And Persistence
GPIO pin configuration and output state are hardware state; the local subdev exists only when Nouveau owns GPIOs outside GSP-RM.

## Dependencies And Integration Points
Depends on DCB GPIO BIOS records, common GPIO base, and `nvkm_gsp_rm` ownership checks.

## Risks And Edge Cases
Incorrect reset decoding can misconfigure GPIO pins. With GSP-RM active, users must rely on RM-managed paths rather than this subdev.

## Test Signals
Correct GPIO setup on GA102 without GSP-RM, `-ENODEV` under GSP-RM, and stable hotplug/power GPIO behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gpio/ga102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gpio/gf119.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gpio/gf119.c

## Purpose
Implements GF119-class GPIO reset, drive, and sense operations.

## Important APIs, Types, And Functions
Exports `gf119_gpio_reset`, `gf119_gpio_drive`, `gf119_gpio_sense`, and `gf119_gpio_new`. Defines a 32-line `nvkm_gpio_func`.

## Control Flow
Reset walks DCB GPIO entries, applies default logical state, writes per-line config at `0x00d610 + line*4`, and may map line numbers through `0x00d740`. Drive sets direction/output bits and triggers an update through `0x00d604`. Sense reads the input bit from the per-line register. Interrupt handling is reused from G94.

## State And Persistence
Hardware pin configuration, drive state, and update trigger bits are modified. Software state is the common GPIO object.

## Dependencies And Integration Points
Uses BIOS DCB records, common GPIO base, and G94 interrupt helpers.

## Risks And Edge Cases
Line numbers come from BIOS and are not range checked in drive/sense. Reset must correctly interpret packed DCB fields.

## Test Signals
Correct GPIO defaults after init, reliable sense/set behavior, and correct event delivery using the G94 interrupt path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gpio/gf119.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gpio/gk104.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gpio/gk104.c

## Purpose
Implements GK104-class GPIO interrupt register layout and local GPIO construction rules.

## Important APIs, Types, And Functions
Defines `gk104_gpio_intr_stat`, `gk104_gpio_intr_mask`, `gk104_gpio` function table, and `gk104_gpio_new`.

## Control Flow
Interrupt status and masks are read/written from `0x00dc00/08` and `0x00dc80/88`, with 16-line packing similar to G94. Drive/sense/reset are reused from GF119. Constructor returns `-ENODEV` if GSP-RM owns the device.

## State And Persistence
Hardware interrupt enable/status state is managed. The common GPIO subdev persists only when constructed.

## Dependencies And Integration Points
Depends on GF119 pin helpers, common GPIO base, and GSP-RM ownership detection.

## Risks And Edge Cases
Interrupt bank packing errors affect GPIO event delivery. Under GSP-RM, local GPIO consumers must not assume this subdev exists.

## Test Signals
Correct hotplug or GPIO events on Kepler-class devices and expected constructor skip with GSP-RM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gpio/gk104.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gpio/nv10.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gpio/nv10.c

## Purpose
Implements NV10-era GPIO drive, sense, and interrupt support for older register layouts.

## Important APIs, Types, And Functions
Defines `nv10_gpio_sense`, `nv10_gpio_drive`, `nv10_gpio_intr_stat`, `nv10_gpio_intr_mask`, `nv10_gpio` function table, and `nv10_gpio_new`.

## Control Flow
Drive/sense choose among register regions based on line ranges: lines 0-1 use `0x600818`, 2-9 use `0x60081c`, and 10-13 use `0x600850`; invalid lines return `-EINVAL`. Interrupt status uses `0x001104` and `0x001144`, splits hi/lo halves, and acknowledges pending bits.

## State And Persistence
The code changes GPIO output/direction bits and interrupt mask/status registers. No additional software state is kept.

## Dependencies And Integration Points
Provides the generation function table consumed by the common GPIO layer.

## Risks And Edge Cases
Line range handling is strict and old hardware register semantics differ from later generations. Wrong line metadata from BIOS can return `-EINVAL` or touch the wrong field.

## Test Signals
Functional GPIO set/get and event delivery on NV10/NV1x hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gpio/nv10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gpio/nv50.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gpio/nv50.c

## Purpose
Implements NV50 GPIO pin reset, drive, sense, and interrupt handling.

## Important APIs, Types, And Functions
Exports `nv50_gpio_reset`, `nv50_gpio_drive`, `nv50_gpio_sense`, and `nv50_gpio_new`. Internal helpers include `nv50_gpio_location`, `nv50_gpio_intr_stat`, and `nv50_gpio_intr_mask`.

## Control Flow
Reset walks DCB GPIO entries, applies default states, and programs auxiliary config bits in `0xe100` or `0xe28c`. Drive/sense map a line under 32 to one of four MMIO registers and a 4-bit field. Interrupt handling reads `0x00e050/54`, splits hi/lo masks, and acknowledges interrupts.

## State And Persistence
Hardware pin state, pin config, and interrupt masks are modified. The common GPIO object stores function table and events.

## Dependencies And Integration Points
Used directly by NV50 and reused by G94 for pin operations. Depends on DCB GPIO BIOS parsing.

## Risks And Edge Cases
Lines 16-31 are locatable for drive/sense, but the NV50 function table advertises 16 interrupt lines. BIOS field interpretation controls reset correctness.

## Test Signals
Correct default GPIO state after init, line sense/drive success, and working 16-line interrupt delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gpio/nv50.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gpio/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gpio/priv.h

## Purpose
Declares private GPIO function-table types and shared generation helper prototypes.

## Important APIs, Types, And Functions
Defines `nvkm_gpio(p)` and `struct nvkm_gpio_func` with line count, interrupt status/mask, drive, sense, and reset hooks. Declares `nvkm_gpio_new_` plus NV50/G94/GF119 helper functions reused across generations.

## Control Flow
No runtime flow; it is the compile-time contract between common base and generation files.

## State And Persistence
No state is stored here. Function tables persist inside constructed `struct nvkm_gpio` objects.

## Dependencies And Integration Points
Includes public `subdev/gpio.h`; generation implementations and `base.c` depend on it.

## Risks And Edge Cases
Hook signatures assume generation code maps line numbers and interrupt masks correctly. Missing mandatory hooks lead to null calls in the base layer.

## Test Signals
Compile/link success and correct dispatch through `gpio->func`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gpio/priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/Kbuild

## Purpose
Builds GSP subdevice support and generation-specific GSP implementations.

## Important APIs, Types, And Functions
Adds `base.o`, `fwsec.o`, generation files from GV100 through GB202, and includes the `rm/` subdirectory.

## Control Flow
Kbuild controls object inclusion for firmware loading, FWSEC boot, and RM-backed GSP support.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Connects GSP core, FWSEC, generation constructors, and RM implementation objects.

## Risks And Edge Cases
Missing objects can break firmware interface discovery or RM support for a generation.

## Test Signals
Kernel build success and available constructors for listed GPU generations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/ad102.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/ad102.c

## Purpose
Defines Ada AD10x GSP function tables, firmware choices, RM GPU-class mapping, and firmware module declarations.

## Important APIs, Types, And Functions
Provides `ad102_gsp`, `ad102_gsps`, and exported `ad102_gsp_new`. It references GA102 Falcon/FWSEC helpers, R535 lifecycle hooks, AD10x signature section, and `ad10x_gpu`.

## Control Flow
Construction delegates to `nvkm_gsp_new_` with firmware interface choices, preferring R570 `570.144` and falling back to R535 `535.113.01`. Lifecycle callbacks then route through TU102/GA102/R535 shared implementations.

## State And Persistence
No custom state beyond the GSP object created by `nvkm_gsp_new_`. Firmware version and RM API selection persist in the selected firmware interface.

## Dependencies And Integration Points
Integrates Ada GSP firmware with RM class tables in `rm/ad10x.c`, R535/R570 RM implementations, and module firmware declarations for AD102/103/104/106/107.

## Risks And Edge Cases
Firmware availability and signature-section matching are critical. Wrong RM GPU class mapping breaks display, FIFO, or engine object allocation.

## Test Signals
Successful firmware load, RM version logging, GSP init/fini, and engine/display operation on AD10x hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/ad102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/base.c

## Purpose
Implements the common GSP subdevice lifecycle, firmware-interface selection, interrupt lookup helpers, and RM state allocation.

## Important APIs, Types, And Functions
Exports `nvkm_gsp_intr_nonstall`, `nvkm_gsp_intr_stall`, `nvkm_gsp_dtor_fws`, `nvkm_gsp_load_fw`, and `nvkm_gsp_new_`. Defines subdev callbacks for oneinit/init/fini/dtor.

## Control Flow
`nvkm_gsp_new_` allocates the GSP object, constructs the subdev, loads a matching firmware interface via `nvkm_firmware_load`, stores `gsp->func`, optionally allocates `gsp->rm` with device, GPU, WPR, and API pointers, and constructs the GSP Falcon. Lifecycle callbacks delegate to selected function hooks. Interrupt helpers search `gsp->intr[]` for stall/nonstall vector data.

## State And Persistence
Persistent state includes selected function table, firmware references, RM object, interrupt table, Falcon object, and running state. Destructor releases firmware references, Falcon state, and RM memory.

## Dependencies And Integration Points
Depends on NVKM firmware loading, Falcon construction, RM interface data, and public GSP structures. Used by all generation constructors.

## Risks And Edge Cases
Required firmware load failure aborts construction. Optional hooks must be checked before use, as the base code does. RM allocations depend on the firmware interface's `rm` pointer and GPU class data.

## Test Signals
Firmware load logs, RM version log, successful Falcon constructor, lifecycle callbacks returning zero, and correct stall/nonstall interrupt lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/fwsec.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/fwsec.c

## Purpose
Builds, patches, boots, and verifies FWSEC Falcon microcode used for secure boot and FRTS setup before or during GSP operation.

## Important APIs, Types, And Functions
Defines firmware interface descriptor unions, DMEM mapper structures, `nvfw_fwsec_frts_cmd`, `nvkm_gsp_fwsec_patch`, `nvkm_gsp_fwsec_v2`, `nvkm_gsp_fwsec_v3`, `nvkm_gsp_fwsec_init`, `nvkm_gsp_fwsec_boot`, `nvkm_gsp_fwsec_sb`, `nvkm_gsp_fwsec_sb_init`, and `nvkm_gsp_fwsec_frts`.

## Control Flow
The init path searches VBIOS PMU entries for FWSEC ucode type `0x85`, reads descriptor version, constructs Falcon firmware from embedded VBIOS data, patches bootloader/signature data depending on descriptor version, sets the DMEM mapper command, and writes read-VBIOS/FRTS command data. Boot calls `nvkm_falcon_fw_boot`; secure-boot and FRTS variants then check mailbox/error registers and log WPR2 ranges for FRTS.

## State And Persistence
It populates temporary or persistent `struct nvkm_falcon_fw` objects, patches firmware image memory, reads BIOS data, and uses GSP `fb.wpr2.frts` state. The FRTS temporary firmware is destroyed after use.

## Dependencies And Integration Points
Depends on VBIOS PMU parsing, `nvfw` blob helpers, Falcon firmware constructors/signing/boot, BIOS signature lookup, and GSP function-table FWSEC hooks.

## Risks And Edge Cases
Descriptor version mismatch, absent DMEM mapper app interface, signature selection failure, or FWSEC mailbox error aborts boot. The code uses `WARN_ON` for malformed firmware structures.

## Test Signals
Successful `fwsec-sb` and `fwsec-frts` boot, zero error mailboxes, and debug output for WPR2 FRTS range.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/fwsec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/ga100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/ga100.c

## Purpose
Defines GA100 GSP Falcon configuration, firmware interface list, RM mapping, and module firmware declarations.

## Important APIs, Types, And Functions
Provides `ga100_gsp_flcn`, `ga100_gsp`, `ga100_gsps`, and `ga100_gsp_new`.

## Control Flow
Constructor delegates to `nvkm_gsp_new_`. Firmware selection tries R570 and R535 RM-capable bootloader firmware and then a no-firmware fallback through `gv100_gsp_nofw`. Lifecycle is shared with TU102/R535 hooks.

## State And Persistence
No unique state beyond selected firmware and GSP object. Falcon register behavior is defined by the static function table.

## Dependencies And Integration Points
Uses GM200/GP102/TU102/GA100 Falcon helpers, TU102 FWSEC, R535 lifecycle, and `ga100_gpu` RM class mapping.

## Risks And Edge Cases
Fallback no-firmware mode means callers must tolerate reduced or absent RM behavior. Incorrect Falcon IRQ/reset settings can prevent boot or interrupt handling.

## Test Signals
Successful firmware selection, GSP boot, and working RM engines on GA100.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/ga100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/ga102.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/ga102.c

## Purpose
Implements GA10x GSP Falcon reset, bootloader construction/signing, FWSEC signature selection, Falcon function table, firmware interface list, and constructor.

## Important APIs, Types, And Functions
Exports `ga102_gsp_reset`, `ga102_gsp_booter_ctor`, `ga102_gsp_fwsec`, `ga102_gsp_flcn`, and `ga102_gsp_new`. Defines RM-capable and no-RM GSP function tables.

## Control Flow
Reset resets the Falcon engine and sets bits at offset `0x1668`. Booter construction parses NVFW bin and HS headers, builds Falcon firmware, signs it using production signatures, maps IMEM/DMEM load regions, and records fuse/engine/ucode IDs. FWSEC signature selection reads fuse version registers and chooses a matching signature index. Firmware selection tries R570, R535, then no-firmware fallback.

## State And Persistence
Booter construction fills a `struct nvkm_falcon_fw`. Selected firmware and RM class mapping persist in `struct nvkm_gsp`.

## Dependencies And Integration Points
Depends on NVFW header parsers, GA102 Falcon DMA/load/boot helpers, BIOS signature data, R535 lifecycle hooks, and `ga1xx_gpu`.

## Risks And Edge Cases
Signature/fuse-version mismatch returns `-EINVAL`. Unsupported engine-id paths return `-ENOSYS`. Firmware format assumptions are strict.

## Test Signals
Successful firmware signing, no fuse-version errors, reset success, and working GSP-RM or no-firmware fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/ga102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/gb100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/gb100.c

## Purpose
Defines GB100/GB10x GSP function table and firmware interface for Blackwell FMC-based boot.

## Important APIs, Types, And Functions
Provides `gb100_gsp`, `gb100_gsps`, and `gb100_gsp_new`. Declares FMC firmware for GB100 and GB102.

## Control Flow
Constructor delegates to `nvkm_gsp_new_`; firmware loading uses `gh100_gsp_load` with R570 RM implementation. Lifecycle uses GH100 oneinit/init/fini and R535 destructor.

## State And Persistence
No custom state beyond the common GSP object and selected RM GPU table `gb10x_gpu`.

## Dependencies And Integration Points
Depends on GH100 FMC boot flow, GA102 Falcon function table, R570 RM API, and GB10x engine class data.

## Risks And Edge Cases
Firmware must contain valid FMC sections and match FSP COT expectations. Missing display class data is intentional for this GPU table and affects available engines.

## Test Signals
Successful FMC firmware load, FSP verification, GSP-FMC boot, and RM initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/gb100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/gb202.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/gb202.c

## Purpose
Defines GB202/GB20x GSP function table and firmware interface for Blackwell desktop-class GPUs.

## Important APIs, Types, And Functions
Provides `gb202_gsp`, `gb202_gsps`, and `gb202_gsp_new`. Declares FMC firmware for GB202/203/205/206/207.

## Control Flow
Construction uses `nvkm_gsp_new_`; firmware loading uses `gh100_gsp_load` with R570 RM metadata. Lifecycle is GH100/R535 based.

## State And Persistence
Common GSP state persists selected firmware and RM GPU table `gb20x_gpu`.

## Dependencies And Integration Points
Integrates with FSP COT boot, GH100 FMC parsing, GA102 Falcon operations, and GB20x display/FIFO/engine class data.

## Risks And Edge Cases
Invalid FMC firmware or COT metadata prevents boot. Wrong class data would affect display and engine allocation on GB20x.

## Test Signals
Successful GSP-FMC boot and working GB20x display/FIFO/engine creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/gb202.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/gh100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/gh100.c

## Purpose
Implements GH100 FMC firmware validation/loading, FSP-assisted GSP-FMC boot, WPR metadata construction, and GH100 GSP lifecycle.

## Important APIs, Types, And Functions
Exports `gh100_gsp_fini`, `gh100_gsp_init`, `gh100_gsp_oneinit`, `gh100_gsp_load`, and `gh100_gsp_new`. Internal helpers validate the FMC ELF image, locate sections, build WPR metadata, and detect GSP lockdown release.

## Control Flow
Oneinit verifies FMC ELF header and section table, validates per-section CRCs, extracts `hash`, `signature`, `publickey`, and `image`, verifies sizes with FSP, copies the FMC image to GSP memory, stores certificate blobs, runs R535 oneinit, and builds WPR metadata. Init prepares or reuses boot args, sets RM descriptor pointers, asks FSP to boot the FMC image, polls for lockdown release and mailbox errors, then starts R535 RM init. Fini shuts down RM and waits for RISC-V halt.

## State And Persistence
Persistent GSP state includes FMC firmware memory, hash/public-key/signature copies, boot args, WPR metadata, framebuffer heap sizing, suspend/resume metadata, and RM state.

## Dependencies And Integration Points
Depends on Linux ELF structures, CRC32, FSP COT boot, framebuffer sizing, R570 GSP structures, R535 RM lifecycle, and GH100/Blackwell firmware packaging.

## Risks And Edge Cases
Strict ELF validation rejects malformed firmware. FSP boot timeouts, mailbox errors, and RISC-V halt timeouts abort init/fini. Resume uses saved metadata and must keep RM args coherent.

## Test Signals
FMC image validation success, FSP COT response, zero boot mailbox, RM init success, and clean RISC-V halt during fini.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/gh100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/gv100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/gv100.c

## Purpose
Provides a no-firmware GV100-style GSP fallback and constructor path used by older or firmwareless configurations.

## Important APIs, Types, And Functions
Defines a minimal GSP function table and exports `gv100_gsp_nofw` and `gv100_gsp_new`.

## Control Flow
The no-firmware loader selects a minimal function table without RM firmware and lets common GSP construction create only the subdev/Falcon pieces needed by the rest of NVKM.

## State And Persistence
Only common GSP subdev state is retained; no RM object is allocated when no RM firmware interface is selected.

## Dependencies And Integration Points
Used as fallback in GA100/GA102 firmware interface arrays and as the GV100 constructor.

## Risks And Edge Cases
Subsystems that require `gsp->rm` must detect its absence. This path is intentionally limited compared with R535/R570 GSP-RM.

## Test Signals
Successful construction without required firmware and correct `nvkm_gsp_rm` false behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/gv100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/priv.h

## Purpose
Declares the private GSP firmware-interface and function-table contracts shared by GSP base, generation files, FWSEC, and RM code.

## Important APIs, Types, And Functions
Declares FWSEC APIs, `struct nvkm_gsp_fwif`, firmware load helpers, firmware declaration macros, `struct nvkm_gsp_func`, generation hooks for TU102/GA102/GH100/R535, and `nvkm_gsp_new_`.

## Control Flow
No runtime flow. It defines how firmware interface arrays select loaders, function tables, RM implementations, and version strings.

## State And Persistence
Function tables and selected firmware interface metadata persist in each GSP object. Firmware declaration macros affect module firmware metadata.

## Dependencies And Integration Points
Includes public `subdev/gsp.h` and RM GPU definitions; links generation code with common GSP and R535 lifecycle helpers.

## Risks And Edge Cases
The table contract is broad and mostly convention-based. Missing hooks must be handled by callers or will lead to null calls in generation paths.

## Test Signals
Compile/link success, firmware interface selection, and correct lifecycle dispatch for all generations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/Kbuild

## Purpose
Builds the generic GSP-RM bridge objects and GPU class tables.

## Important APIs, Types, And Functions
Includes `client.o`, `engine.o`, `gr.o`, `nvdec.o`, `nvenc.o`, generation GPU table files, and the `r535/` subdirectory.

## Control Flow
Kbuild compiles common RM object wrappers, engine constructors, and per-generation class constants.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Connects RM client/object machinery with R535/R570 APIs and generation GSP function tables.

## Risks And Edge Cases
Omitted object files can produce missing RM class mappings or engine constructors.

## Test Signals
Build success and availability of RM-backed engines for supported GSP-RM GPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/ad10x.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/ad10x.c

## Purpose
Defines Ada AD10x RM class IDs and FIFO doorbell behavior for RM-backed Nouveau objects.

## Important APIs, Types, And Functions
Exports `ad10x_gpu` as `struct nvkm_rm_gpu`, filling display, usermode, FIFO channel, CE, GR, NVDEC, NVENC, and OFA class IDs.

## Control Flow
No dynamic flow. RM engine/display/fifo constructors read this table when creating objects.

## State And Persistence
The table is immutable generation metadata.

## Dependencies And Integration Points
Uses NVIF class IDs and `tu102_chan_doorbell_handle`. Referenced by `ad102_gsp`.

## Risks And Edge Cases
Incorrect class IDs cause RM allocation failures or wrong engine classes exposed to userspace.

## Test Signals
Successful display channel creation, FIFO channel allocation, and CE/GR/video engine object allocation on AD10x.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/ad10x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/client.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/client.c

## Purpose
Manages GSP-RM client ID allocation, construction, and destruction.

## Important APIs, Types, And Functions
Exports `nvkm_gsp_client_ctor` and `nvkm_gsp_client_dtor`.

## Control Flow
Constructor requires `gsp->rm`, allocates an ID from `gsp->client_id.idr`, initializes client backpointers and event list, and calls the selected RM API client constructor with handle `NVKM_RM_CLIENT(id)`. Destructor frees the RM client object if allocated, removes the ID under mutex, and clears `client->gsp`.

## State And Persistence
Persists IDR entries, client object handle, event list, and GSP backpointer until destruction.

## Dependencies And Integration Points
Depends on RM API `client->ctor`, GSP RM allocation/free helpers, and `handles.h` handle encoding.

## Risks And Edge Cases
ID allocation failure aborts construction. Destruction must run after dependent events/objects are freed to avoid dangling event callbacks.

## Test Signals
Unique client handles, successful RM root allocation, and clean IDR removal during teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/engine.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/engine.c

## Purpose
Provides generic RM-backed NVKM engine and engine-object construction for CE, GR, NVDEC, NVENC, NVJPG, and OFA engines.

## Important APIs, Types, And Functions
Defines `struct nvkm_rm_engine`, `struct nvkm_rm_engine_obj`, `nvkm_rm_engine_obj_new`, `nvkm_rm_engine_ctor`, `nvkm_rm_engine_new`, and internal object destructors/constructors.

## Control Flow
Engine construction builds an `nvkm_engine_func` with supported class entries, each using `nvkm_rm_engine_obj_ctor`. Object construction dispatches by engine type to the relevant RM API allocation hook or generic `nvkm_gsp_rm_alloc` for GR. `nvkm_rm_engine_new` maps requested NVKM engine type/instance to the device engine slot and generation class ID, special-casing GR and unsupported MiG GR instances.

## State And Persistence
Engine function tables and RM objects persist while engines/objects exist. Object destructors free RM handles.

## Dependencies And Integration Points
Depends on `nvkm_rm_gpu` class tables, FIFO channels, RM API engine allocators, and NVKM engine/object frameworks.

## Risks And Edge Cases
Instance bounds are checked for device arrays. Unsupported engine types return `-ENODEV`; GR instance other than 0 is ignored. Missing class IDs or RM API hooks cause allocation failures.

## Test Signals
Engine subdev creation, successful userspace object allocation for each class, and RM object free on destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/engine.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/engine.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/engine.h

## Purpose
Declares the shared RM-backed engine constructor interface.

## Important APIs, Types, And Functions
Declares `nvkm_rm_engine_ctor`, `nvkm_rm_engine_new`, `nvkm_rm_engine_obj_new`, `nvkm_rm_gr_new`, `nvkm_rm_nvdec_new`, and `nvkm_rm_nvenc_new`.

## Control Flow
No runtime flow. It exposes constructors to common RM, GR, and video engine files.

## State And Persistence
No state is stored here.

## Dependencies And Integration Points
Includes `gpu.h` and links generic engine construction with GR/video wrappers.

## Risks And Edge Cases
The declarations assume callers pass valid RM, class, and instance data. Implementation enforces most runtime checks.

## Test Signals
Compile/link success and correct use by RM engine files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/engine.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/ga100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/ga100.c

## Purpose
Defines GA100 RM class IDs for compute/datacenter Ampere devices.

## Important APIs, Types, And Functions
Exports `ga100_gpu` with usermode, FIFO channel, CE, GR, and NVDEC class IDs.

## Control Flow
No dynamic flow. RM constructors consume the static table.

## State And Persistence
Immutable class metadata.

## Dependencies And Integration Points
Referenced by `ga100_gsp`; uses NVIF class constants and TU102 doorbell helper.

## Risks And Edge Cases
No display/NVENC/OFA classes are supplied here. Incorrect class values break RM object allocation.

## Test Signals
Successful FIFO, CE, GR, compute, and NVDEC object creation on GA100.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/ga100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/ga1xx.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/ga1xx.c

## Purpose
Defines GA10x RM class IDs for Ampere display, FIFO, graphics, copy, decode, encode, and OFA engines.

## Important APIs, Types, And Functions
Exports `ga1xx_gpu` as `struct nvkm_rm_gpu`.

## Control Flow
Static class data is read by RM-backed display, FIFO, and engine constructors.

## State And Persistence
Immutable generation metadata.

## Dependencies And Integration Points
Referenced by GA102 GSP RM function table. Uses NVIF class IDs and TU102 FIFO doorbell helper.

## Risks And Edge Cases
Bad class IDs cause RM allocation failures visible during display or engine initialization.

## Test Signals
Working display channels, FIFO channels, GR/CE/video object creation on GA10x.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/ga1xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/gb10x.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/gb10x.c

## Purpose
Defines GB10x RM class IDs for Blackwell datacenter-style GPUs.

## Important APIs, Types, And Functions
Exports `gb10x_gpu` with Hopper usermode, Blackwell FIFO channel, CE, GR/compute, NVDEC, NVJPG, and OFA classes.

## Control Flow
No runtime flow; constructors consume the table.

## State And Persistence
Immutable RM class metadata.

## Dependencies And Integration Points
Referenced by GB100 GSP function table. Uses TU102 doorbell helper for FIFO channels.

## Risks And Edge Cases
Display classes are absent; display construction should not expect them. Wrong Blackwell class IDs break RM allocations.

## Test Signals
Successful FIFO, CE, GR, NVDEC, NVJPG, and OFA object allocation on GB10x.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/gb10x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/gb20x.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/gb20x.c

## Purpose
Defines GB20x RM class IDs and generation-specific FIFO/CE behavior for Blackwell display GPUs.

## Important APIs, Types, And Functions
Exports `gb20x_gpu` with display, usermode, FIFO channel, CE, GR, NVDEC, NVENC, NVJPG, and OFA class IDs. Uses `gb202_chan_doorbell_handle` and `gb202_ce_grce_mask`.

## Control Flow
No dynamic control flow. RM constructors use the table to allocate objects and to skip certain GRCE engines in FIFO setup.

## State And Persistence
Immutable class and callback metadata.

## Dependencies And Integration Points
Referenced by GB202 GSP function table; integrates with Blackwell FIFO and CE helper code.

## Risks And Edge Cases
Incorrect GRCE mask or doorbell callback affects channel creation and runlist selection. Display class mismatches break RM display init.

## Test Signals
Working GB20x display init, FIFO channel creation, and engine allocation across display/video/graphics/copy engines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/gb20x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/gh100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/gh100.c

## Purpose
Defines GH100 RM class IDs for Hopper GSP-RM devices.

## Important APIs, Types, And Functions
Exports `gh100_gpu` with usermode, FIFO channel, CE, GR/compute, NVDEC, NVJPG, and OFA classes.

## Control Flow
Static metadata is consumed by RM-backed FIFO and engine constructors.

## State And Persistence
Immutable generation class table.

## Dependencies And Integration Points
Referenced by `gh100_gsp`; uses TU102 channel doorbell helper.

## Risks And Edge Cases
No display classes are provided. Wrong class IDs fail RM engine allocations.

## Test Signals
Successful Hopper FIFO channel and engine object allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/gh100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/gpu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/gpu.h

## Purpose
Declares the RM GPU class metadata structure used by GSP-RM constructors.

## Important APIs, Types, And Functions
Defines `struct nvkm_rm_gpu` with display, usermode, FIFO, CE, GR, NVDEC, NVENC, NVJPG, and OFA class/callback fields. Declares external tables for TU1xx, GA100, GA1xx, AD10x, GH100, GB10x, and GB20x.

## Control Flow
No runtime flow. The selected GSP firmware function table points `gsp->rm->gpu` to one of these tables.

## State And Persistence
The selected table persists in `struct nvkm_rm` and drives object allocation throughout device lifetime.

## Dependencies And Integration Points
Included by RM engine/display/FIFO code and generation class table files.

## Risks And Edge Cases
Zero class fields indicate unavailable functionality only if callers handle them. Incorrect callbacks or class IDs break RM allocations.

## Test Signals
Correct class exposure and successful RM object construction across all table users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/gpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/gr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/gr.c

## Purpose
Creates the RM-backed graphics engine wrapper and routes graphics class object construction through RM allocations.

## Important APIs, Types, And Functions
Defines `nvkm_rm_gr_new`, `nvkm_rm_gr_obj_ctor`, `nvkm_rm_gr_init`, and `nvkm_rm_gr_fini`.

## Control Flow
`nvkm_rm_gr_new` builds an `nvkm_gr_func` with I2M, 2D, 3D, and compute classes from `rm->gpu->gr.class`, sets R535 GR hooks for oneinit, units, and channel creation, allocates `struct r535_gr`, and installs it as `device->gr`. Init/fini optionally call RM API scrubber hooks.

## State And Persistence
Persists the graphics engine object, its function table, R535 context buffer metadata, and scrubber channel state.

## Dependencies And Integration Points
Depends on `r535_gr_*` functions, RM GPU class tables, NVKM GR engine framework, FIFO channels, and RM object allocation helpers.

## Risks And Edge Cases
Class table entries must be valid. Scrubber hooks are optional. GR context buffer metadata is populated in R535 oneinit and must match RM expectations.

## Test Signals
Successful GR engine creation, graphics/compute object allocation, context promotion, and scrubber init/fini if present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/gr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/gr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/gr.h

## Purpose
Declares R535 graphics-engine private state used by generic RM GR and R535 GR implementation files.

## Important APIs, Types, And Functions
Defines `R515_GR_MAX_CTXBUFS`, `struct r535_gr_chan`, `struct r535_gr`, and `r535_gr_get_ctxbuf_info`.

## Control Flow
No runtime flow. Structures describe per-channel context buffers, global context buffers, and scrubber objects.

## State And Persistence
`r535_gr` stores context buffer descriptors, shared global context memory, and scrubber channel/object state. `r535_gr_chan` stores VMM references and per-channel context memory/VMA arrays.

## Dependencies And Integration Points
Included by generic RM GR and R535 GR files; depends on NVKM memory, VMM, object, and GR types.

## Risks And Edge Cases
`R515_GR_MAX_CTXBUFS` bounds all context buffer arrays; overflow is guarded by implementation `WARN_ON`s. Lifetime of VMM mappings must match channel destruction.

## Test Signals
No context buffer overflow warnings, clean VMM/memory unrefs, and successful graphics context creation/destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/gr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/handles.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/handles.h

## Purpose
Defines Nouveau-local RM object handle constants and encodings.

## Important APIs, Types, And Functions
Provides macros such as `NVKM_RM_CLIENT(id)`, `NVKM_RM_CLIENT_MASK`, `NVKM_RM_DEVICE`, `NVKM_RM_SUBDEVICE`, `NVKM_RM_DISP`, `NVKM_RM_VASPACE`, `NVKM_RM_CHAN(chid)`, and `NVKM_RM_THREED`.

## Control Flow
No runtime flow. Handles are embedded in RM allocation and free messages.

## State And Persistence
Handle values persist as identifiers for allocated RM objects until freed.

## Dependencies And Integration Points
Used by RM client, device, display, FIFO, GR, VMM, and engine code to create stable RM object hierarchies.

## Risks And Edge Cases
Handle collisions can corrupt RM object ownership. Client IDs must stay within `NVKM_RM_CLIENT_MASK`.

## Test Signals
No RM allocation conflicts, successful free of handles, and correct IDR client removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/handles.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/nvdec.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/nvdec.c

## Purpose
Creates RM-backed NVDEC engine wrappers.

## Important APIs, Types, And Functions
Defines `nvkm_rm_nvdec_dtor` and exports `nvkm_rm_nvdec_new`.

## Control Flow
Constructor calls `nvkm_rm_engine_ctor` with the generation NVDEC class and installs the result into `device->nvdec[inst]`. Destructor frees the engine function table.

## State And Persistence
Persists an NVKM engine object and function table while the engine exists.

## Dependencies And Integration Points
Depends on generic RM engine construction and `rm->gpu->nvdec.class`.

## Risks And Edge Cases
Missing or zero class IDs cause unusable NVDEC allocation paths. Instance bounds are checked by caller `nvkm_rm_engine_new`.

## Test Signals
Successful NVDEC engine creation and userspace decoder object allocation/free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/nvdec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/nvenc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/nvenc.c

## Purpose
Creates RM-backed NVENC engine wrappers.

## Important APIs, Types, And Functions
Defines `nvkm_rm_nvenc_dtor` and exports `nvkm_rm_nvenc_new`.

## Control Flow
Constructor delegates to `nvkm_rm_engine_ctor` with the generation NVENC class and stores the engine in `device->nvenc[inst]`. Destructor frees the generated function table.

## State And Persistence
The engine object persists in the device NVENC array until teardown.

## Dependencies And Integration Points
Depends on generic RM engine helpers and `rm->gpu->nvenc.class`.

## Risks And Edge Cases
Devices without NVENC class support should not route here. Bad class IDs fail RM allocations.

## Test Signals
Successful NVENC engine creation and video encoder class allocation/free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/nvenc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/Kbuild

## Purpose
Builds the R535/R570-style RM API implementation objects used by GSP-RM.

## Important APIs, Types, And Functions
Includes RM core, GSP, RPC, control/allocation/client/device, BAR, FBSR, VMM, display, FIFO, CE, GR, and video/OFA object files.

## Control Flow
Kbuild compiles all R535 API modules into NVKM so firmware-interface records can point at R535/R570 RM API tables.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Connects lower-level RM RPC/control wrappers to display, FIFO, memory, and engine implementations.

## Risks And Edge Cases
Omitted modules can leave function pointers unresolved or null in RM API tables.

## Test Signals
Build success and full GSP-RM feature availability at runtime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/alloc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/alloc.c

## Purpose
Implements R535 RM object allocation and free RPC wrappers.

## Important APIs, Types, And Functions
Defines `r535_gsp_rpc_rm_alloc_get`, `r535_gsp_rpc_rm_alloc_push`, `r535_gsp_rpc_rm_alloc_done`, `r535_gsp_rpc_rm_free`, and exports `r535_alloc`.

## Control Flow
Allocation get builds an `NV_VGPU_MSG_FUNCTION_GSP_RM_ALLOC` RPC with client, parent, object handle, class, and parameter size, returning the parameter payload. Push submits it, checks RM status, converts errors with `r535_rpc_status_to_errno`, logs non-retry failures, and releases the RPC. Free sends `NV_VGPU_MSG_FUNCTION_FREE` with root and object handles.

## State And Persistence
RM object handles persist in `struct nvkm_gsp_object` until freed. RPC buffers are transient and returned to the GSP RPC layer.

## Dependencies And Integration Points
Used by all R535 RM object constructors through generic `nvkm_gsp_rm_alloc_*` helpers. Depends on RPC functions and NVRM allocation structures.

## Risks And Edge Cases
RPC allocation failure maps to `-EIO` or pointer errors. RM retry statuses are intentionally not logged as hard errors. Free depends on valid client/object relationships.

## Test Signals
Successful RM object allocations, meaningful RM_ALLOC error logs, and no leaked RM handles on teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/alloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/bar.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/bar.c

## Purpose
Adapts GF100 BAR handling for GSP-RM ownership, including BAR1/BAR2 page-directory handoff and BAR2 flush behavior.

## Important APIs, Types, And Functions
Defines `r535_bar_flush`, `r535_bar_bar2_update_pde`, BAR1/BAR2 init/fini/wait callbacks, `r535_bar_dtor`, and `r535_bar_new_`.

## Control Flow
BAR2 init reads Nouveau's BAR2 PDB entry, sends it to RM with `UPDATE_BAR_PDE`, records RM BAR2 PDB state in the VMM, maps a zero VRAM page as a flush target, and switches flushes to BAR2. BAR2 fini restores physical-mode flushing and clears the RM PDE. BAR1 init replaces the VMM root page directory memory with RM-provided BAR1 PDB memory. Constructor wraps a hardware BAR function table and ioremaps physical BAR2 for early/resume flushing.

## State And Persistence
Persists BAR function table, `flushBAR2`, `flushBAR2PhysMode`, `flushFBZero`, BAR1/BAR2 VMM page-directory memory, and `bar2` state. RM also stores BAR PDE state.

## Dependencies And Integration Points
Depends on GF100 BAR code, RAM wrapping, VMM page tables, GSP RPC control, framebuffer memory, and device resource mapping.

## Risks And Edge Cases
BAR2 flush is needed before BAR2 page tables are restored on resume. Failed zero-page mapping or PDE update is warned. Incorrect PDB handoff breaks CPU/GPU memory mappings.

## Test Signals
Successful BAR init/fini, no BAR2 flush faults across resume, valid BAR1/BAR2 mappings, and no `UPDATE_BAR_PDE` warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/bar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/ce.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/ce.c

## Purpose
Allocates R535 RM copy-engine objects.

## Important APIs, Types, And Functions
Defines `r535_ce_alloc` and exports `r535_ce` as an `nvkm_rm_api_engine`.

## Control Flow
Allocation obtains CE parameters from `nvkm_gsp_rm_alloc_get`, sets version 1 and `engineType` to `NV2080_ENGINE_TYPE_COPY0 + inst`, then writes the allocation RPC.

## State And Persistence
The created RM CE object persists through the supplied `nvkm_gsp_object`.

## Dependencies And Integration Points
Called by generic RM engine object construction for CE classes.

## Risks And Edge Cases
Instance-to-engineType mapping assumes contiguous RM copy engine IDs. Allocation parameter retrieval can fail.

## Test Signals
Successful CE object allocation for each exposed copy engine instance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/ce.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/client.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/client.c

## Purpose
Implements R535 RM root client allocation.

## Important APIs, Types, And Functions
Defines `r535_gsp_client_ctor` and exports `r535_client`.

## Control Flow
The constructor allocates an `NV01_ROOT` object with `NV0000_ALLOC_PARAMETERS`, sets `hClient` to the chosen client handle and `processID` to all bits set, then submits the allocation.

## State And Persistence
The root RM client object persists in `client->object` until the generic client destructor frees it.

## Dependencies And Integration Points
Called by `nvkm_gsp_client_ctor`; uses R535 allocation wrappers and NVRM client definitions.

## Risks And Edge Cases
Failure to allocate the root client prevents all child RM objects. Process ID is synthetic and must be acceptable to RM firmware.

## Test Signals
Successful RM client constructor and later child device/subdevice allocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/ctrl.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/ctrl.c

## Purpose
Implements R535 RM control RPC get/push/done wrappers.

## Important APIs, Types, And Functions
Defines `r535_gsp_rpc_rm_ctrl_get`, `r535_gsp_rpc_rm_ctrl_push`, `r535_gsp_rpc_rm_ctrl_done`, and exports `r535_ctrl`.

## Control Flow
Get creates a `GSP_RM_CONTROL` RPC with client handle, object handle, command ID, and parameter size, returning the parameter payload. Push sends the RPC, converts RM status to errno, optionally returns reply parameters for caller inspection, or completes the RPC immediately. Done releases a retained reply.

## State And Persistence
Control RPC buffers are transient. Object and client handles identify persistent RM objects.

## Dependencies And Integration Points
Used by display, FIFO, GR, FBSR, BAR, and device event code for control commands.

## Risks And Edge Cases
Callers must call done when push returns reply parameters. Nonzero RM status is logged except retry/busy cases. `NULL` params are tolerated in done.

## Test Signals
Successful control calls, correct error propagation, and no leaked RPC buffers during repeated display/FIFO operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/ctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/device.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/device.c

## Purpose
Implements R535 RM device/subdevice creation and RM event registration.

## Important APIs, Types, And Functions
Defines device constructor/destructor, subdevice constructor, event constructor/destructor, notification enable helper, and exports `r535_device`.

## Control Flow
Device construction allocates `NV01_DEVICE_0` under a client, then `NV20_SUBDEVICE_0` under the device. Event construction allocates `NV01_EVENT_KERNEL_CALLBACK_EX`, enables repeated notification via `NV2080_CTRL_CMD_EVENT_SET_NOTIFICATION`, then links the callback into the client's event list under the GSP client mutex. Destruction unlinks events and frees RM objects.

## State And Persistence
Persists RM device, subdevice, and event objects plus event callback list entries until explicit destructor calls.

## Dependencies And Integration Points
Used by display, FBSR, VMM, and internal GSP-RM setup. Depends on RM allocation/control APIs and client event lists.

## Risks And Edge Cases
Event callbacks must be unlinked before freeing objects. Partial construction must free parent objects on failure.

## Test Signals
Successful device/subdevice allocation, hotplug/IRQ event callbacks firing, and clean teardown without stale event callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/disp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/disp.c

## Purpose
Implements the R535 RM-backed display engine, including display channels, output discovery, SOR/DP/HDMI/audio/backlight controls, hotplug/DP IRQ events, and vblank interrupt routing.

## Important APIs, Types, And Functions
Defines channel helpers for core/window/immediate/cursor channels, `r535_disp_chan_set_pushbuf`, `r535_dmac_alloc`, SOR HDMI/DP/HDA/backlight function tables, connector/output creation helpers, DP AUX/training/MST helpers, display event callbacks, `r535_disp_oneinit/init/fini/dtor`, `r535_disp_new`, and exports `r535_disp` API.

## Control Flow
Oneinit allocates display RAMIN, tells internal RM about instance memory, constructs RM client/device/display-common objects, queries static display info, optionally forwards ACPI brightness state, enables manual DisplayPort mode, queries head count/mask, creates head and SOR objects, queries supported display IDs, creates outputs/connectors through RM control calls, initializes an NVKM event object, registers RM hotplug and DP IRQ events, builds RAMHT, and registers a stall interrupt handler. Runtime channel init sets pushbuffer metadata with RM and allocates the corresponding RM channel object. Output operations call RM controls for detection, SOR assignment, active output inheritance, EDID, DP AUX, DP training, MST IDs, HDMI SCDC/audio, and backlight.

## State And Persistence
Persists display instance memory, RM client/device/object handles, `objcom`, hotplug/IRQ event handles, assigned SOR mask, heads, SORs, connectors, outputs, RAMHT, channel `suspend_put` offsets, and NVKM event state. Hardware vblank masks and display channel user areas are touched.

## Dependencies And Integration Points
Depends on NVKM display/head/IOR/output/channel frameworks, GSP RM allocation/control/device-event APIs, ACPI DSM for brightness data, RAMHT, VFN interrupt handling, and generation RM GPU display class data.

## Risks And Edge Cases
The file contains many RM protocol assumptions. Display ID to SOR inheritance must match RM state. DP AUX/training includes retry handling for RM-requested panel delays. Missing ACPI or RM support paths must fail gracefully. Channel suspend offsets are captured from MMIO and reused on resume.

## Test Signals
Working mode setting, hotplug and DP IRQ events, vblank interrupts, DP AUX/training, MST allocation, HDMI/DP audio, backlight get/set, suspend/resume channel restoration, and clean RM object teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/disp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/fbsr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/fbsr.c

## Purpose
Implements R535 framebuffer save/restore support and an RM-aware instmem wrapper for suspend/resume.

## Important APIs, Types, And Functions
Defines `struct fbsr_item`, `struct fbsr`, `r535_fbsr_memlist`, `fbsr_init`, `fbsr_send`, `r535_fbsr_suspend`, `r535_fbsr_resume`, `r535_fbsr`, `r535_instmem_new`, and its destructor.

## Control Flow
Suspend builds a list of VRAM regions to preserve from instmem preserved objects, boot objects, and the GSP non-WPR heap. It totals region sizes, adds reserved framebuffer and VGA workspace sizes, allocates a scatter-gather sysmem buffer, creates a temporary RM client/device, registers sysmem with RM, then sends each VRAM region as a memory-list object and control command. Resume frees the sysmem buffer because RM has restored VRAM. `r535_fbsr_memlist` builds RM memory-list RPCs for host or framebuffer memory.

## State And Persistence
During suspend it persists `gsp->sr.fbsr` sysmem backup until resume. Temporary RM client/device/memory-list objects are freed after setup. Instmem wrapper disables zeroing while preserving hardware hooks.

## Dependencies And Integration Points
Depends on instmem lists, GSP SG allocation, RM device/client APIs, RM control commands, memory target/address helpers, and NV50 instmem construction.

## Risks And Edge Cases
Missing preserved regions can lose VRAM state across suspend. Memory-list page counts assume GSP page size alignment. Failure after sysmem allocation must free backup storage.

## Test Signals
Successful suspend with FBSR debug region logs, successful resume without VRAM corruption, and no SG memory leaks on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/fbsr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/fifo.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/fifo.c

## Purpose
Implements R535 RM-backed FIFO, runlist, channel allocation, engine discovery, channel error recovery, and constructed Falcon context sizing.

## Important APIs, Types, And Functions
Defines channel callbacks, `r535_chan_alloc`, `r535_chan_ramfc_write/clear`, engine functions for CE/GR/Falcon engines, `r535_fifo_rc_chid`, `r535_fifo_rc_triggered`, `r535_fifo_xlat_rm_engine_type`, `r535_fifo_ectx_size`, `r535_fifo_runl_ctor`, `r535_fifo_new`, and exports `r535_fifo`.

## Control Flow
Runlist construction allocates CHID/CGID spaces, queries RM's device info table, creates runlists, translates RM engine IDs to NVKM types/instances, skips unsupported SW engines and lone GRCEs, creates RM-backed engines, adds them to runlists, stores engine descriptors, queries CE fault method buffer size, and fetches constructed Falcon context sizes. Channel RAMFC write allocates a coherent method buffer, calls RM channel allocation with instance/userd/ramfc/method/gpfifo data, binds the engine, and schedules the GPFIFO. RC notifications log RM exception data and mark the channel in error.

## State And Persistence
Persists FIFO function table, runlists, engines, CHID allocators, channel RM objects, method buffers, GR context refs, engine RM descriptors/sizes, and nonstall interrupt state.

## Dependencies And Integration Points
Depends on NVKM FIFO/runlist/channel frameworks, GSP internal RM controls, RM GPU class/callback data, GR context constructors, DMA coherent allocation, and GSP interrupt lookup.

## Risks And Edge Cases
RM engine translation must be complete. Method buffer allocation cleanup depends on `ramfc_clear`. GR contexts take extra refs until channel deletion. Device info table changes can expose unsupported engine types.

## Test Signals
Successful runlist construction, channel creation/scheduling, workload execution, RC error reporting, and clean channel teardown without memory leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/fifo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/gr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/gr.c

## Purpose
Implements R535 graphics context buffer discovery, golden context initialization, per-channel context promotion, and GR teardown.

## Important APIs, Types, And Functions
Defines `r535_gr_promote_ctx`, `r535_gr_chan_new`, `r535_gr_units`, `r535_gr_get_ctxbuf_info`, `r535_gr_get_ctxbufs_and_zcull_info`, `r535_gr_oneinit`, `r535_gr_dtor`, and exports `r535_gr`.

## Control Flow
Oneinit allocates a golden instance object and VMM, creates an RM VA space and privileged channel, queries RM for context buffer sizes, allocates/promotes golden context buffers, allocates a 3D object to trigger RM golden-context initialization, then frees temporary objects while retaining global context buffers. Per-channel creation references the channel VMM and calls `r535_gr_promote_ctx` to allocate or reuse context buffers, map them into the VMM, and send `GPU_PROMOTE_CTX` entries to RM. Destructor frees per-channel mappings and global context memory.

## State And Persistence
`r535_gr` stores context buffer descriptors and global context buffer memory. Each `r535_gr_chan` stores VMM refs, memory refs, and VMA mappings until channel object destruction. `r535_gr_units` reports GPC/TPC state from GSP.

## Dependencies And Integration Points
Depends on RM internal static GR context queries, RM FIFO channel allocation, RM VMM VA-space creation, NVKM memory/VMM APIs, and graphics class allocation.

## Risks And Edge Cases
Context buffer arrays are bounded by `R515_GR_MAX_CTXBUFS`. Memory/VMM mapping failures during promotion can leave partially allocated resources handled by object teardown. RM context metadata must match expected buffer ID mapping.

## Test Signals
Successful golden context initialization, graphics channel creation, no context buffer warnings, correct GPC/TPC unit reporting, and clean context memory unrefs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/gr.c -->
