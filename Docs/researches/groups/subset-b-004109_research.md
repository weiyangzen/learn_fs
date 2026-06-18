<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttv-driver.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttv-driver.c

## Purpose
`bttv-driver.c` is the main V4L2 PCI driver for Brooktree/Conexant Bt848/Bt849/Bt878/Bt879 frame grabber chips. It owns module parameters, PCI probe/remove, chip initialization, V4L2 video/radio/VBI device registration, video buffer queues, analog input/audio routing, crop/standard management, IRQ handling, suspend/resume, and DVB subdevice autoload for cards with a digital transport path.

## Important APIs, Types, And Functions
The file exports global driver state `bttv_num`, `bttvs[]`, `bttv_debug`, `bttv_verbose`, and `bttv_gpio`. Probe entry is `bttv_probe()`, removal is `bttv_remove()`, module setup is `bttv_init_module()`, and PCI registration is via `bttv_pci_driver`. The main V4L2 surface is `bttv_video_template` with `bttv_fops` and `bttv_ioctl_ops`; radio uses `radio_template`, `radio_fops`, and `radio_ioctl_ops`. Buffer lifecycle hooks are `queue_setup()`, `buf_prepare()`, `buf_queue()`, `start_streaming()`, and `stop_streaming()`. Format and geometry ioctls include `bttv_try_fmt_vid_cap()`, `bttv_s_fmt_vid_cap()`, `bttv_g_selection()`, and `bttv_s_selection()`. The chip-control path includes `set_tvnorm()`, `set_input()`, `video_mux()`, `audio_input()`, `audio_mute()`, `set_pll()`, `bt848A_set_timing()`, `init_irqreg()`, and `init_bt848()`.

## Control Flow
Module initialization clamps capture-buffer parameters, checks PCI chipset quirks, registers the custom `bttv-sub` bus, then registers the PCI driver. `bttv_probe()` allocates and initializes `struct bttv`, enables PCI/MMIO/DMA, registers the V4L2 device, creates controls, identifies the board, requests the shared IRQ, initializes RISC/DMA and GPIO, runs card-specific initialization, registers I2C and tuner/audio subdevices, registers video/VBI/radio nodes, adds a DVB subdevice for boards with `has_dvb`, and optionally starts IR support. Runtime capture flows from V4L2 queue setup through `bttv_buffer_risc()` in `bttv-risc.c`; queued buffers cause DMA to start when the queue was empty. RISCI interrupts switch active video/VBI RISC hooks, complete old buffers, and advance sequence/timestamps. Timeout recovery tears down active DMA and marks outstanding buffers done/error.

## State And Persistence
Persistent in-memory state lives in `struct bttv`: current norm/input/frequency, controls, crop defaults/current crop, video/VBI resource ownership, active and queued buffers, IRQ counters, radio state, GPIO state, I2C state, and suspend snapshot. Hardware state is mirrored into Bt848 registers through `btwrite()` and recovered after reset/resume by `bttv_reinit_bt848()`. There is no disk persistence; module parameters and device state are reset on module unload or reprobe.

## Dependencies And Integration Points
This file integrates with PCI, V4L2 core, videobuf2 DMA-SG, media controller subdev calls, I2C subdevices, tuner/audio chips, rc-core IR support, and companion bttv files. It calls card tables from `bttv-cards.c`, RISC routines from `bttv-risc.c`, VBI routines from `bttv-vbi.c`, I2C setup from `bttv-i2c.c`, GPIO helpers from `bttv-gpio.c`, and input helpers from `bttv-input.c`. DVB support is triggered through `bttv_sub_add_device(&btv->c, "dvb")` and async `request_module("dvb-bt8xx")`.

## Risks
High-risk areas are IRQ/DMA races under `s_lock`, line ownership between VBI and video crop windows, hardware register programming during active capture, and legacy compatibility paths that intentionally permit overlap-like VBI settings while hardware truncates capture. `bttv_irq()` disables interrupt masks on lockup, so regressions can silently stop capture. Probe error paths have many resources to unwind; missed cleanup would leak IRQ/MMIO/V4L2 state. Format and crop calculations rely on chip limits and field semantics; off-by-one errors can corrupt DMA programs or reject valid userspace requests.

## Test Signals
Useful signals are successful PCI probe logs, registered `/dev/video*`, `/dev/vbi*`, and optional `/dev/radio*` nodes, `VIDIOC_QUERYCAP`, format negotiation across packed/planar/raw formats, VBI and video concurrent-stream rejection/acceptance according to line windows, radio tuner frequency operations, suspend/resume with active queues, IRQ counters without lockup messages, and successful buffer completion under `v4l2-compliance`, `qv4l2`, or capture tools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttv-driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttv-gpio.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttv-gpio.c

## Purpose
`bttv-gpio.c` provides two services: a small `bttv-sub` bus for in-kernel bt8xx subdrivers, and exported GPIO register accessors for code that needs to manipulate Bt848/Bt878 GPIO pins through a `struct bttv_core`.

## Important APIs, Types, And Functions
The central bus object is `bttv_sub_bus_type`, with match/probe/remove callbacks `bttv_sub_bus_match()`, `bttv_sub_probe()`, and `bttv_sub_remove()`. Device lifecycle helpers are `bttv_sub_add_device()` and `bttv_sub_del_devices()`. External subdrivers register through `bttv_sub_register()` and `bttv_sub_unregister()`, both exported. GPIO APIs are `bttv_gpio_inout()`, `bttv_gpio_read()`, `bttv_gpio_write()`, and `bttv_gpio_bits()`.

## Control Flow
The main bttv probe path initializes `core->subs` and calls `bttv_sub_add_device()` for DVB-capable cards. That allocates `struct bttv_sub_device`, attaches it to the parent PCI device and `bttv-sub` bus, names it as `<name><nr>`, registers it, and links it into the core list. Driver registration stores the wanted name prefix, and bus matching compares device names against that prefix. Removal iterates the linked subdevice list, unregistering each device.

## State And Persistence
Subdevice state is represented by dynamically allocated `struct bttv_sub_device` objects linked from `struct bttv_core.subs`; release frees them after the device core drops references. GPIO state is hardware register state in `BT848_GPIO_OUT_EN` and `BT848_GPIO_DATA`; writes are immediate and not persisted outside the device.

## Dependencies And Integration Points
This file depends on Linux device-core bus/driver registration, bttv private register helpers from `bttvp.h`, and the shared `struct bttv_core`/`struct bttv_sub_driver` definitions from `bttv.h`. DVB integration uses this bus so `dvb-bt8xx` can bind to a logical subdevice created by the analog bttv driver.

## Risks
The bus match is prefix-based, so overly broad `wanted` strings can bind unintended subdevices. GPIO direction/data updates are partially protected: direction and masked data writes use `gpio_lock`, but full `bttv_gpio_write()` does not, so callers must avoid racing masked writes. Subdevice list management assumes device-core callbacks do not reenter in a way that mutates the list unexpectedly.

## Test Signals
Expected signals are successful `bus_register()` in module init, `add subdevice "dvbN"` logs for DVB cards, successful subdriver probe/remove callbacks, and correct GPIO read/write behavior verified through card-specific hooks, DVB startup, audio muxing, or external subdrivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttv-gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttv-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttv-i2c.c

## Purpose
`bttv-i2c.c` implements the Bt848/Bt878 I2C adapter used to discover and control EEPROMs, tuners, audio processors, IR receivers, and other board subdevices. It supports both software bit-bang I2C over the chip pins and Bt878 hardware I2C transactions.

## Important APIs, Types, And Functions
Module parameters are `i2c_debug`, `i2c_hw`, `i2c_scan`, and `i2c_udelay`. Bit-bang callbacks are `bttv_bit_setscl()`, `bttv_bit_setsda()`, `bttv_bit_getscl()`, and `bttv_bit_getsda()` through `bttv_i2c_algo_bit_template`. Hardware transfer routines are `bttv_i2c_wait_done()`, `bttv_i2c_sendbytes()`, `bttv_i2c_readbytes()`, and `bttv_i2c_xfer()` through `bttv_algo`. Public helpers are `bttv_I2CRead()`, `bttv_I2CWrite()`, `bttv_readee()`, `init_bttv_i2c()`, and `fini_bttv_i2c()`.

## Control Flow
`init_bttv_i2c()` chooses hardware mode if forced or configured by the board; otherwise it installs an `i2c-algo-bit` adapter after raising SCL/SDA. Hardware transfers program `BT848_I2C`, clear/observe `BT848_INT_I2CDONE` and `BT848_INT_RACK`, and wait on `btv->i2c_queue`, which is woken by `bttv_irq()` when an I2CDONE interrupt arrives. Optional scan probes all 7-bit addresses and reports known mappings. `fini_bttv_i2c()` deletes the adapter when registration succeeded.

## State And Persistence
State is kept in `btv->c.i2c_adap`, `btv->i2c_client`, `btv->i2c_algo`, `btv->i2c_state`, `btv->i2c_rc`, `btv->i2c_done`, and `btv->i2c_queue`. It is initialized during PCI probe and destroyed on remove. EEPROM reads are caller-supplied buffers only; no persistent storage is modified.

## Dependencies And Integration Points
The file integrates with Linux I2C core, `i2c-algo-bit`, V4L2 device private data, the bttv IRQ handler, `tveeprom_read()`, tuner/audio/IR clients, and board identification in `bttv-cards.c`. The hardware adapter depends on I2CDONE interrupts being enabled by `init_irqreg()`.

## Risks
Hardware I2C waits are interrupt-driven and can fail if IRQs are masked or the chip is wedged. `bttv_i2c_wait_done()` treats RACK as success and timeout/no-RACK as failure; subtle changes could break device probing. The helper functions mutate the shared `btv->i2c_client.addr`, so concurrent users need serialization at higher layers. Too-small `i2c_udelay` is clamped, but unusual boards may still be timing-sensitive.

## Test Signals
Signals include adapter registration under `/sys/bus/i2c`, optional `i2c_scan` discoveries, successful EEPROM reads, tuner/audio subdevice binding, IR receiver probing, no `i2c read/write error` warnings during probe, and working frequency/audio controls through V4L2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttv-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttv-if.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttv-if.c

## Purpose
`bttv-if.c` preserves the old exported GPIO/kernel-module interface for consumers that address bttv cards by card index instead of using the newer `bttv-sub` device model. The source comments mark it obsolete in favor of `bttv-gpio.c`.

## Important APIs, Types, And Functions
The exported symbols are `bttv_get_pcidev()`, `bttv_gpio_enable()`, `bttv_read_gpio()`, and `bttv_write_gpio()`. These functions operate on the global `bttvs[]` array and the current `bttv_num` card count, then delegate to `gpio_inout()`, `gpio_read()`, and `gpio_bits()` macros.

## Control Flow
Callers pass a card index. Each function checks the index against `bttv_num`, verifies the `struct bttv *` exists, and returns `-EINVAL` or `-ENODEV` when invalid. GPIO enable updates `BT848_GPIO_OUT_EN`, read returns `BT848_GPIO_DATA`, and write updates masked data bits. Debug tracking is emitted when `bttv_gpio` is enabled.

## State And Persistence
There is no state local to this file. It exposes global live driver state and hardware GPIO registers. `bttv_read_gpio()` additionally rejects access after `btv->shutdown` is set during remove, reducing use-after-remove risk for legacy clients.

## Dependencies And Integration Points
This interface depends on `bttv-driver.c` maintaining `bttvs[]`, `bttv_num`, and `shutdown`. It shares register access helpers and GPIO locking behavior with `bttv-gpio.c`. Legacy IR or board helper modules may still use these symbols.

## Risks
The interface is card-index based and lacks device references, so users can race hot-unplug/removal unless they handle `-ENODEV`. `bttv_gpio_enable()` and `bttv_write_gpio()` do not check `shutdown`, unlike read. Because the interface is deprecated, test coverage may be weaker than for the subdevice path.

## Test Signals
Signals are module symbol availability, successful legacy client load, correct negative returns for invalid card numbers or removed devices, and GPIO tracking logs showing expected masked updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttv-if.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttv-input.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttv-input.c

## Purpose
`bttv-input.c` implements infrared remote-control support for selected bttv boards. It handles GPIO-polled remotes, GPIO IRQ remotes, a legacy GPIO RC5 decoder for Nebula DigiTV, and I2C IR receiver instantiation for cards with external IR chips.

## Important APIs, Types, And Functions
Entry points called by the main driver are `init_bttv_i2c_ir()`, `bttv_input_init()`, `bttv_input_fini()`, and `bttv_input_irq()`. GPIO key paths are `ir_handle_key()` and `ir_enltv_handle_key()`. RC5 handling uses `bttv_rc5_irq()`, `bttv_rc5_timer_end()`, and `bttv_rc5_decode()`. I2C IR support includes `get_key_pv951()` and `i2c_new_scanned_device()` setup. Runtime state is `struct bttv_ir` from `bttvp.h` plus an `rc_dev`.

## Control Flow
During bttv probe, `init_bttv_i2c_ir()` may instantiate an `ir_video` I2C client, then `bttv_input_init()` selects masks, polling interval, keymap, or RC5 mode based on `btv->c.type`. It configures GPIO direction, allocates/registers an rc-core device, and starts polling or RC5 completion timers. Interrupts from the main bttv IRQ handler call `bttv_input_irq()`, which dispatches to RC5 or GPIO decoding. Polling timers periodically read GPIO, extract keycode bits, and emit `rc_keydown*()`/`rc_keyup()`.

## State And Persistence
Remote state includes key masks, last GPIO value, RC5 bit accumulation, base timestamp, active flag, timer, keymap name, and rc-core device. The state lasts for the PCI device lifetime and is freed by `bttv_input_fini()`. No persistent configuration is stored beyond module parameters `ir_debug` and `ir_rc5_remote_gap`.

## Dependencies And Integration Points
This file depends on `rc-core`, Linux input, I2C client creation, bttv GPIO helpers, bttv board IDs/keymaps, and the main IRQ path. It requests `ir-kbd-i2c` when built as a module. Remote capability is advertised by card tables via `has_remote`.

## Risks
The board switch hardcodes many GPIO masks and keymaps; wrong masks cause stuck keydown, missing keyup, or noisy input. RC5 decoding is deliberately legacy and timing-sensitive, using GPIO edge timing and a timer endpoint. `bttv_input_fini()` unregisters and then frees the rc device pointer, so lifecycle changes must respect rc-core ownership. Poll intervals as low as 1 ms can increase CPU wakeups on affected hardware.

## Test Signals
Expected signals are registered rc-core devices with correct keymaps, `ir-keytable` visibility, key events from GPIO and I2C remotes, no repeated stuck keys, correct RC5 toggle handling on Nebula DigiTV, and clean teardown without timer warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttv-input.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttv-risc.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttv-risc.c

## Purpose
`bttv-risc.c` builds and manages Bt848 RISC DMA programs for video and VBI capture, calculates scaler/crop register geometry, hooks active per-buffer programs into the persistent main RISC loop, and starts/stops DMA according to active buffers.

## Important APIs, Types, And Functions
Program generators are `bttv_risc_packed()` and internal `bttv_risc_planar()`. Geometry routines are `bttv_calc_geo_old()`, `bttv_calc_geo()`, and `bttv_apply_geo()`. Main-loop and DMA functions are `bttv_risc_init_main()`, `bttv_risc_hook()`, `bttv_set_dma()`, `bttv_start_dma()`, and `bttv_stop_dma()`. Buffer-specific paths are `bttv_buffer_risc()`, `bttv_buffer_risc_vbi()`, `bttv_buffer_activate_video()`, and `bttv_buffer_activate_vbi()`.

## Control Flow
Probe calls `bttv_risc_init_main()` to allocate one page containing a loop with sync and jump slots for odd/even VBI and video fields. Buffer prepare builds per-buffer RISC instructions over the vb2 DMA-SG scatterlist, splitting writes across SG segment boundaries and accounting for packed, planar, raw, interlaced, single-field, and sequential field layouts. IRQ-time activation unlinks selected buffers from queues, applies geometry/color registers, patches main-loop jump slots to point at buffer programs, and sets IRQ flags so the hardware returns control at frame/VBI boundaries. `bttv_set_dma()` updates loop IRQ status, watchdog timer, capture control bits, and FIFO/RISC enable bits.

## State And Persistence
RISC memory is allocated in `struct btcx_riscmem` fields for `btv->main` and each `struct bttv_buffer` top/bottom field. Active state is `btv->curr`, `btv->cvbi`, `btv->loop_irq`, and `btv->dma_on`, protected by `s_lock` in callers. Geometry is stored in each buffer so IRQ activation can program registers without recalculating.

## Dependencies And Integration Points
The file depends on `btcx-risc` allocation helpers, videobuf2 DMA-SG plane descriptors, bttv TV norms/formats/crop state, Bt848 register definitions, and the main IRQ code in `bttv-driver.c`. VBI queueing in `bttv-vbi.c` and video queueing in `bttv-driver.c` both call into these routines.

## Risks
RISC program size estimates and SG walking are memory-safety critical; underestimation or bad offsets can overrun the allocated program or program invalid DMA addresses. Multiple assignments to `r` in `bttv_buffer_risc()` can overwrite an earlier field generation error if later generation succeeds. The VCR hack skips trailing lines, which can surprise format-size assumptions. Activation occurs in IRQ-sensitive contexts and must keep main-loop jump slots consistent with hardware execution.

## Test Signals
Signals include successful buffer prepare for every supported pixel format/field mode, stable streaming without SCERR/OCERR/FDSR messages, correct image geometry after crop/standard changes, VBI data completion, and watchdog timer not firing under normal capture. Debug RISC disassembly should show coherent sync/write/jump sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttv-risc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttv-vbi.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttv-vbi.c

## Purpose
`bttv-vbi.c` implements the V4L2 VBI capture queue and VBI format negotiation for bttv devices. It coordinates VBI line windows with video crop windows and builds VBI RISC programs through `bttv-risc.c`.

## Important APIs, Types, And Functions
The exported queue ops are `bttv_vbi_qops`, whose callbacks are `queue_setup_vbi()`, `buf_prepare_vbi()`, `buf_queue_vbi()`, `buf_cleanup_vbi()`, `start_streaming_vbi()`, and `stop_streaming_vbi()`. V4L2 ioctl helpers are `bttv_try_fmt_vbi_cap()`, `bttv_s_fmt_vbi_cap()`, `bttv_g_fmt_vbi_cap()`, and `bttv_vbi_fmt_reset()`. Internal `try_fmt()` clamps line starts/counts and fills VBI sampling metadata.

## Control Flow
VBI queue setup sizes buffers from `count[0] + count[1]` times `samples_per_line`. Prepare validates the plane size, marks field none, and calls `bttv_buffer_risc_vbi()`. Queueing starts VBI DMA when the VBI queue was empty, sharing `loop_irq` with active video streaming if needed. `start_streaming_vbi()` claims `RESOURCE_VBI`, resets IRQ state when video is not streaming, and returns queued buffers on conflict. Format setting rejects changes while VBI resources are held, clamps to the current TV norm and `crop_start`, updates `btv->vbi_fmt`, and records `end`, the earliest video line boundary.

## State And Persistence
VBI state is stored in `btv->vbiq`, `btv->vbi_fmt`, `btv->vbi_count[]`, `btv->vcapture`, and active `btv->cvbi`. `bttv_vbi_fmt_reset()` initializes default lines and maintains compatibility buffer size `VBI_BPL * VBI_DEFLINES * 2`. There is no disk persistence.

## Dependencies And Integration Points
This file depends on V4L2/videobuf2, bttv TV norm metadata (`vbistart`, `Fsc`, crop bounds), resource helpers in `bttv-driver.c`, RISC generation in `bttv-risc.c`, and IRQ completion in `bttv-driver.c`. The compatibility behavior is tied to older bttv userspace expectations.

## Risks
The code intentionally preserves legacy semantics where userspace may request overlapping VBI/video windows even though hardware aborts VBI at video start. Incorrect `crop_start`/`vbi_end` handling can allow VBI and video capture to compete for the same scan lines. The fixed `VBI_BPL` compatibility size can hide that the chip writes fewer samples per line. Queue conflict paths must return buffers in a state that vb2 userspace can recover from.

## Test Signals
Useful tests are `VIDIOC_TRY_FMT`/`S_FMT` VBI across PAL/NTSC norms, VBI read and streaming modes, VBI plus video concurrent capture with non-overlapping line windows, resource conflict returns, correct sequence stamping, and no timeout when only VBI streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttv-vbi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttv.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttv.h

## Purpose
`bttv.h` is the public-ish bttv interface header used by other in-kernel drivers and bttv companion files. It defines card IDs, board configuration structures, exported legacy GPIO APIs, the newer subdevice bus interface, GPIO helpers, I2C helper declarations, and IR entry points.

## Important APIs, Types, And Functions
Major types are `struct bttv_core`, `struct tvcard`, `struct bttv_sub_device`, and `struct bttv_sub_driver`. The header declares card setup hooks `bttv_idcard()`, `bttv_init_card1()`, `bttv_init_card2()`, `bttv_init_tuner()`, chipset hooks, legacy GPIO functions, subdriver registration, GPIO accessors, I2C helpers, and input helper functions. It defines many `BTTV_BOARD_*` constants and the compile-time `MUXSEL()` macro family used by board tables.

## Control Flow
The header does not execute code, but its types shape the runtime flow. `struct bttv_core` is embedded at the start of private `struct bttv` and shared with subdrivers. `struct tvcard` entries drive muxing, GPIO audio routing, tuner configuration, video input counts, DVB/remote/radio capability, and card-specific hooks. `bttv_call_all()` and `bttv_call_all_err()` wrap V4L2 subdevice broadcasts.

## State And Persistence
The header defines state containers rather than storing state itself. `struct tvcard` is static board metadata. `struct bttv_core` carries per-device V4L2, PCI, I2C, subdevice list, number, and card type. GPIO and subdevice structures point back to this core.

## Dependencies And Integration Points
It depends on V4L2, I2C, tuner definitions, and media device APIs. It is included by bttv implementation files, bt8xx DVB modules, and legacy external users of the bttv GPIO interface. Board table definitions in `bttv-cards.c` rely heavily on the board IDs and `struct tvcard`.

## Risks
The large board-ID namespace is ABI-like inside the driver family; reordering or changing IDs breaks board tables and module parameters. `MUXSEL()` uses preprocessor packing with octal literal tricks, so callers must pass plain 0-3 digits. The header exposes obsolete legacy GPIO functions that can keep unsafe usage patterns alive.

## Test Signals
Compile coverage is the main signal. Runtime signals include correct card identification by board ID, mux selection matching board tables, successful subdriver registration, and external modules resolving the declared symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttvp.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttvp.h

## Purpose
`bttvp.h` is the private bttv implementation header. It centralizes internal constants, structures, function prototypes, debug macros, hardware register access macros, and the full `struct bttv` device state used by the driver files.

## Important APIs, Types, And Functions
Important types include `struct bttv_tvnorm`, `struct bttv_format`, `struct bttv_ir`, `struct bttv_geometry`, `struct bttv_buffer`, `struct bttv_buffer_set`, `struct bttv_vbi_fmt`, `struct bttv_crop`, `struct bttv_pll_info`, `struct bttv_suspend_state`, and `struct bttv`. It declares internal functions for VBI, RISC, GPIO, input, I2C, resource allocation, and IRQ register initialization. Register macros are `btwrite()`, `btread()`, `btand()`, `btor()`, and `btaor()`.

## Control Flow
The header describes how companion files interlock: queue callbacks use `struct bttv_buffer`, RISC code uses `RISC_SLOT_*` constants, resource checks use `RESOURCE_*`, VBI code uses `VBI_BPL`/`VBI_DEFLINES`, and IRQ/DMA paths manipulate `struct bttv.curr`, `cvbi`, `loop_irq`, and `timeout`. `to_bttv()` converts from `struct v4l2_device` to the enclosing driver object.

## State And Persistence
`struct bttv` is the authoritative in-memory state object. It contains PCI/MMIO identity, card configuration, GPIO/I2C/subdevice state, V4L2 device nodes, control handlers, remote state, locks, frequencies, norm/crop/format state, buffer queues, active DMA state, timeout/watchdog state, suspend snapshot, and statistics. No persistent state is defined.

## Dependencies And Integration Points
The header includes kernel PCI/I2C/input/mutex/scatterlist/device headers, V4L2 controls/fh/common, videobuf2 DMA-SG, tveeprom, rc-core, `ir-kbd-i2c`, TEA575x, and local `bt848.h`, `bttv.h`, and `btcx-risc.h`. It is intentionally private to bttv implementation files and should not be used by unrelated modules.

## Risks
Because this header defines the core state shape, changes have wide blast radius across video, VBI, I2C, IRQ, GPIO, and input paths. Register access macros assume a local variable named `btv`; using them in the wrong scope is error-prone. Locking expectations are documented in comments but not enforced by types, especially around RISC state and crop/resource fields.

## Test Signals
Compile and sparse-style checking catch many header breakages. Runtime signals include successful probe/remove, stable capture, no lockdep complaints around documented locks, working suspend/resume state restoration, and correct interaction between video and VBI queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttvp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/dst.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/dst.c

## Purpose
`dst.c` is the DVB frontend/card driver for TwinHan DST devices attached through bt878 hardware. It implements the private DST/RDC 8820 command protocol over bt878 GPIO-assisted PIO and I2C, identifies the board/firmware/tuner, configures transport packet size, and exposes DVB frontend operations for DVB-S, DVB-T, DVB-C, and ATSC variants.

## Important APIs, Types, And Functions
Exported functions are `rdc_reset_state()`, `dst_pio_disable()`, `dst_wait_dst_ready()`, `dst_error_recovery()`, `dst_error_bailout()`, `dst_comm_init()`, `write_dst()`, `read_dst()`, `dst_check_sum()`, and `dst_attach()`. Core internal paths include `dst_gpio_outb()`, `dst_gpio_inb()`, `rdc_8820_reset()`, `dst_command()`, `dst_probe()`, `dst_get_device_id()`, `dst_write_tuna()`, `dst_get_tuna()`, and DVB ops such as `dst_set_frontend()`, `dst_tune_frontend()`, `dst_read_status()`, `dst_set_voltage()`, `dst_set_tone()`, and `dst_set_diseqc()`.

## Control Flow
`dst_attach()` receives an allocated `struct dst_state`, calls `dst_probe()`, then copies the frontend ops matching detected `dst_type`. Probe optionally resets CA daughterboard hardware, initializes PIO, requests device ID via a fixed 8-byte command, matches firmware strings against `dst_tlist`, discovers tuner type/capabilities, requests MAC/firmware/card/vendor information when supported, and sets TS packet size to 204 when required. Tuning updates `state->tx_tuna` based on delivery system, frequency, symbol rate, bandwidth, modulation, FEC, voltage, tone, and DiSEqC state, then sends it through the DST command protocol and reads back lock/frequency.

## State And Persistence
`struct dst_state` persists frontend state: tx/rx command buffers, detected type flags/features, current frontend properties, DiSEqC/power flags, decode lock/strength/SNR, firmware strings, tuner/card/vendor info, `dst_mutex`, and optional CA device pointer. Hardware state exists in the DST ASIC, bt878 GPIO lines, and TS packet-size control. There is no disk persistence.

## Dependencies And Integration Points
This file depends on Linux DVB frontend APIs, `bt878_device_control()` from the bt878 bridge, I2C transfer APIs, `dst_common.h`/`dst_priv.h`, and optional CA attachment handled by `dst_ca.c` from release cleanup. The frontend is typically instantiated by `dvb-bt8xx`.

## Risks
The communication protocol is timing-sensitive, with sleeps, PIO toggles, ACK bytes, checksum validation, and recovery resets. Device identification falls back to satellite/symdiv defaults for unknown strings, which can misconfigure unsupported hardware. Several board capability paths are firmware-string-specific. Mutex coverage is vital because CA and frontend paths share the same DST command channel. Tuning status is partly cached, so stale lock state is possible if command recovery fails.

## Test Signals
Signals include successful `dst_attach()`, recognized firmware/model logs, TS188/TS204 selection, DVB frontend registration with the correct delivery system, successful tuning/lock for supported satellite/terrestrial/cable/ATSC inputs, valid signal strength/SNR reads, DiSEqC/voltage/tone behavior on satellite cards, and recovery from transient I2C/PIO errors without wedging the frontend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/dst.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/dst_ca.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/dst_ca.c

## Purpose
`dst_ca.c` implements the DVB conditional-access device for DST cards with CI/CA capability. It translates Linux DVB CA ioctls into DST CI command packets, sends them over the shared DST communication channel, and returns slot/application/CA information to userspace.

## Important APIs, Types, And Functions
The exported attach point is `dst_ca_attach()`, which registers a `DVB_DEVICE_CA`. File operations are `dst_ca_fops` with `dst_ca_ioctl()`, open/release/read/write stubs, and `noop_llseek`. CI protocol helpers include `put_command_and_length()`, `put_checksum()`, `dst_ci_command()`, `dst_put_ci()`, `ca_get_app_info()`, `ca_get_ca_info()`, `ca_get_slot_caps()`, `ca_get_slot_info()`, `ca_get_message()`, `ca_send_message()`, `ca_set_pmt()`, `dst_check_ca_pmt()`, `handle_dst_tag()`, `write_to_8820()`, and `asn_1_decode()`.

## Control Flow
Userspace opens the DVB CA device and issues ioctls. `dst_ca_ioctl()` serializes all CA ioctls through `dst_ca_mutex`, allocates temporary CA structures, obtains `struct dst_state` from `dvbdev->priv`, and dispatches standard CA commands. `CA_SEND_MSG` parses EN50221 tags and either sends CA PMT, CA PMT reply, app-info enquiry, or CA-info enquiry. `CA_GET_MSG` copies cached transformed responses from `state->messages`. Slot/capability ioctls send fixed DST commands, decode selected fields, and copy Linux CA structures back to userspace. Low-level commands lock `state->dst_mutex`, initialize DST communication, write command bytes, disable PIO, read ACK, optionally wait and read a reply buffer, and retry up to `RETRIES`.

## State And Persistence
The file uses global `dst_ca_mutex` for ioctl serialization and shared `state->messages[256]` as the cached message/reply buffer. The registered `struct dvb_device` stores `dst_state` as private data, and `state->dst_ca` points back to the device. No persistent storage is used.

## Dependencies And Integration Points
It depends on DVB CA UAPI structures, `dvb_register_device()`, frontend state from `dst_common.h`, and the exported DST communication helpers in `dst.c`. `dst.c` release unregisters `state->dst_ca` when present. CA support is gated by card capabilities and module-side attachment by the DVB bridge.

## Risks
This code handles userspace buffers and variable-length CA messages, so copy bounds and length validation are critical. Some paths are incomplete (`ca_get_slot_descr()` returns `-EOPNOTSUPP`, CA PMT reply support is stub-like), and several packet transformations assume specific DST firmware response layouts. `ca_set_pmt()` uses decoded ASN.1 length to clear/build buffers; malformed lengths can stress the fixed 256-byte message capacity despite checks in `handle_dst_tag()`. The CA and frontend paths share `state->dst_mutex`, so deadlocks or long sleeps affect tuning responsiveness.

## Test Signals
Signals include successful CA device registration, `CA_GET_CAP`, `CA_GET_SLOT_INFO`, `CA_SEND_MSG` with app/CA enquiries, `CA_GET_MSG` returning transformed EN50221 messages, CAM insertion/removal flag changes, PMT delivery to a CAM, and no `-EFAULT`/`-EIO` under valid userspace ioctls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/dst_ca.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/dst_ca.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/dst_ca.h

## Purpose
`dst_ca.h` defines DST conditional-access protocol constants and a small private wrapper for the DST CA device. It is shared by `dst_ca.c` and `dst_common.h`.

## Important APIs, Types, And Functions
The header defines retry count `RETRIES` and EN50221-style CA tag constants such as `CA_APP_INFO_ENQUIRY`, `CA_APP_INFO`, `CA_INFO_ENQUIRY`, `CA_INFO`, `CA_PMT`, `CA_PMT_REPLY`, and MMI/menu/list/keypad tags under `0x9f88xx`. `struct dst_ca_private` groups a `struct dst_state *` and `struct dvb_device *`.

## Control Flow
No code executes here. The tag definitions drive `ca_send_message()` and `ca_get_message()` switch statements in `dst_ca.c`, and `RETRIES` bounds low-level CI communication retry loops.

## State And Persistence
The header defines a possible state wrapper but does not allocate or persist state. Runtime CA state actually lives in `struct dst_state` and `struct dvb_device`.

## Dependencies And Integration Points
It forward-references `struct dst_state` indirectly through usage and is included by `dst_common.h`, which exposes `dst_ca_attach()`. The constants align Linux DVB CA ioctl message payloads with the DST CI packet translation layer.

## Risks
Incorrect tag values would route CA messages to the wrong handler or make userspace/CAM negotiation fail. The unused `dst_ca_private` structure can mislead maintainers because the active implementation stores `dst_state` directly in `dvb_device.priv`.

## Test Signals
Compile coverage and successful CA ioctl dispatch for app info, CA info, PMT, and MMI tags validate this header. Retry behavior is indirectly tested by transient CI command failures recovering before `RETRIES`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/dst_ca.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/dst_common.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/dst_common.h

## Purpose
`dst_common.h` is the shared DST frontend/CA contract. It defines device type constants, feature flags, tuner flags, GPIO/PIO command values, communication constants, the central `struct dst_state`, board/tuner descriptor structs, and exported function prototypes.

## Important APIs, Types, And Functions
Important constants include `DST_TYPE_IS_SAT/TERR/CABLE/ATSC`, type flags such as `DST_TYPE_HAS_TS188`, `DST_TYPE_HAS_TS204`, `DST_TYPE_HAS_FW_*`, `DST_TYPE_HAS_MULTI_FE`, and `DST_TYPE_HAS_VLF`, capability flags such as `DST_TYPE_HAS_CA`, `DST_TYPE_HAS_DISEQC*`, and `DST_TYPE_HAS_ANALOG`, tuner flags, RDC 8820 GPIO values, `GET_REPLY`, `GET_ACK`, `FIXED_COMM`, and `ACK`. Major types are `struct dst_state`, `struct tuner_types`, `struct dst_types`, and `struct dst_config`.

## Control Flow
The header does not execute, but `struct dst_state` is passed through all frontend and CA operations. Its fields are filled during `dst_probe()`, read and updated during tuning/status calls, shared with CA ioctls, and freed in the frontend release callback. Prototypes expose the low-level communication helpers across `dst.c` and `dst_ca.c`.

## State And Persistence
`struct dst_state` contains the entire runtime state for a DST frontend: bridge/I2C/config pointers, frontend object, tx/rx buffers, detected device type/capability flags, current tuning and DiSEqC parameters, decoded signal metrics, message buffers, identity strings, mutex, firmware name, and optional CA device. It is volatile kernel memory only.

## Dependencies And Integration Points
The header depends on DVB frontend and device types, Linux mutexes, local `bt878.h`, and `dst_ca.h`. It is the integration point between `dvb-bt8xx`, `dst.c`, and `dst_ca.c`.

## Risks
Many flags use overlapping bit values in separate namespaces (`type_flags`, `dst_hw_cap`, tuner types), so using a flag in the wrong field can silently misconfigure behavior. Fixed-size buffers such as `tx_tuna[10]`, `rxbuffer[10]`, `messages[256]`, and short identity strings require strict length discipline in protocol code. Exposing communication helpers means CA and frontend code must coordinate locking around `dst_mutex`.

## Test Signals
Compile coverage across DST modules, correct board-type detection, correct frontend ops selection, CA attachment for CA-capable cards, and valid signal/tuning state transitions all validate this shared contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/dst_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/dst_priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/dst_priv.h

## Purpose
`dst_priv.h` defines the private GPIO-control packet interface between the DST frontend driver and the bt878 bridge. It is the low-level bridge contract used by `dst.c` to enable pins, write output levels, read input levels, and set transport packet size.

## Important APIs, Types, And Functions
The header defines `struct dst_gpio_enable`, `struct dst_gpio_output`, `struct dst_gpio_read`, and `union dst_gpio_packet`. Command IDs are `DST_IG_ENABLE`, `DST_IG_WRITE`, `DST_IG_READ`, and `DST_IG_TS`. It forward declares `struct bt878` and declares `bt878_device_control(struct bt878 *bt, unsigned int cmd, union dst_gpio_packet *mp)`.

## Control Flow
No executable code lives here. `dst_gpio_outb()` in `dst.c` fills `union dst_gpio_packet.enb` for `DST_IG_ENABLE` and `.outp` for `DST_IG_WRITE`; `dst_gpio_inb()` uses `.rd` with `DST_IG_READ`; `dst_packsize()` passes `.psize` with `DST_IG_TS`. The bt878 bridge interprets these commands to manipulate hardware.

## State And Persistence
The packet structs are transient call arguments. Persistent state is in the bt878 bridge and hardware GPIO/TS configuration, not in this header.

## Dependencies And Integration Points
This header bridges `dst.c` and the bt878 implementation. It is intentionally narrower than the public bttv GPIO APIs because DST needs command-style access to bt878-specific GPIO and transport settings.

## Risks
The union relies on the command ID matching the active member; using the wrong member corrupts the bridge request. `dst_gpio_read.value` is `unsigned long` while DST code truncates to `u8`, so bridge-side changes to meaningful high bits would be lost. The header lacks include guards, so repeated inclusion depends on current include patterns not causing redefinition problems.

## Test Signals
Signals include successful DST reset/PIO enable/disable/readiness checks, correct TS188/TS204 packet-size selection, no `bt878_device_control` errors during probe and tuning, and valid GPIO readback during DST handshakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/dst_priv.h -->
