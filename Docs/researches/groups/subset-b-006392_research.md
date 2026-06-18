# subset-b-006392 ALSA PCI driver research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/cthw20k2.c -->
# sources/distributed-fs/ceph-client/sound/pci/ctxfi/cthw20k2.c

## Purpose

This file implements the EMU20K2/X-Fi hardware backend behind `struct hw`. It translates the generic ctxfi resource, mixer, DAIO, timer, DAC/ADC, transport, and power-management operations into MMIO register programming for 20k2-family Creative cards, including Titanium HD (`CTSB1270`) and Onkyo SE-300PCIE (`CTOK0010`) model differences.

## Important APIs, types, and functions

The exported constructors are `create_20k2_hw_obj()` and `destroy_20k2_hw_obj()`. The central object is `struct hw20k2`, which embeds `struct hw` and stores I2C addressing state plus `mic_source`. The static `ct20k2_preset` fills the hardware vtable: SRC control block allocators and setters, SRC manager enable/disable, SRCIMP mapper programming, AMIXER setters, DAI/DAO and DAIO manager operations, timer IRQ/tick accessors, card init/stop, ADC source selection, output/mic switches, suspend/resume, and raw MMIO helpers. Major internal control blocks include `src_rsc_ctrl_blk`, `src_mgr_ctrl_blk`, `srcimp_mgr_ctrl_blk`, `amixer_rsc_ctrl_blk`, `dai_ctrl_blk`, `dao_ctrl_blk`, and `daio_mgr_ctrl_blk`.

## Control flow

`hw_card_init()` starts PCI/MMIO/IRQ access with `hw_card_start()`, initializes PLL and auto-init, resets interrupt state, programs GPIO, enables the audio ring, initializes device virtual memory transport from `card_conf.vm_pgt_phys`, configures DAIO clocks/ports, initializes DAC and ADC codecs, then enables audio-ring input into SRC. Resource code above it follows a dirty-bit model: generic setters update cached control blocks, and commit functions write only dirty registers. SRC commit also clears zero buffers and programs parameter mixer pitch; DAIO commit walks transmitter/receiver dirty masks; I2C helpers unlock the chip, poll data-ready, then read/write external codecs.

## State and persistence behavior

Persistent driver state is in `struct hw20k2`, `struct hw`, hardware registers, cached resource control blocks, IRQ callback fields, MMIO mappings, and PCI region ownership. Dirty flags preserve intended register state until commit. `hw_output_switch_put()` persists output route in GPIO extended data; `hw_mic_source_switch_put()` persists the selected mic source in `hw20k2->mic_source` and WM8775 registers. Suspend stops hardware; resume reruns full card initialization from the supplied card configuration.

## Dependencies and integration points

It depends on `cthardware.h` contracts, `ct20k2reg.h` register offsets, Linux PCI/MMIO/IRQ/DMA APIs, and ctxfi resource managers in `ctsrc`, `ctamixer`, `ctdaio`, `cttimer`, and `ctatc`. `xfi.c` and ATC creation select this backend for 20k2 cards. The timer layer uses `set_timer_irq()`, `set_timer_tick()`, and `get_wc()`. Mixer controls call capability, output switch, mic source, ADC source, and SPDIF status functions through the ATC layer.

## Risks and test signals

Key risks are register bitfield drift, busy waits without timeouts in some polling paths, model-specific GPIO mistakes, I2C lock/unlock failures, missing cleanup after partial `hw_card_init()` failure, DMA mask fallback behavior, IRQ callback races during shutdown, and the static assumptions around 4K page-table pages. Test signals include successful probe/register/remove on each supported subsystem, playback/capture at 44.1/48/96/192 kHz as applicable, SPDIF status changes, ADC source switching, Titanium HD output/mic controls, suspend/resume restoration, IRQ delivery, and `dmesg` absence of PLL/auto-init/I2C errors.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/cthw20k2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/cthw20k2.h -->
# sources/distributed-fs/ceph-client/sound/pci/ctxfi/cthw20k2.h

## Purpose

This header exposes the 20k2 hardware-object lifecycle to the rest of the ctxfi driver.

## Important APIs, types, and functions

It includes `cthardware.h` and declares `create_20k2_hw_obj(struct hw **rhw)` plus `destroy_20k2_hw_obj(struct hw *hw)`. The implementation returns a heap-allocated `struct hw20k2` through its embedded `struct hw`.

## Control flow

ATC setup includes this header when selecting a hardware backend. Creation allocates and initializes a vtable preset; destruction shuts down the card if still mapped and frees the object.

## State and persistence behavior

The header owns no state. It defines the constructor boundary for the persistent `struct hw` state implemented in `cthw20k2.c`.

## Dependencies and integration points

It is coupled to `cthardware.h` and the ATC hardware selection path. Its small API hides 20k2-specific fields from generic ctxfi modules.

## Risks and test signals

The main risk is lifecycle mismatch: callers must destroy only objects created by this backend. Build coverage of 20k2 support and probe/remove tests catch signature or ownership regressions.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/cthw20k2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctimap.c -->
# sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctimap.c

## Purpose

This file implements generic circular input-mapper list management used to program hardware mapper RAM for resources such as SRCIMP.

## Important APIs, types, and functions

`input_mapper_add()` inserts an `imapper` ordered by input slot and updates the new entry plus the predecessor through a caller-supplied `map_op`. `input_mapper_delete()` removes an entry, rewires the predecessor to the next entry, and clears the single-node case. `free_input_mapper_list()` deletes and frees every mapper node on a list.

## Control flow

Add handles the empty list by making the entry point to itself, otherwise scans by slot, inserts before the first larger slot or at the tail, computes predecessor and successor with wraparound, then invokes `map_op` for changed entries. Delete computes wraparound predecessor and successor; a one-node list is zeroed and unmapped, while multi-node removal updates the predecessor before deleting the target.

## State and persistence behavior

State is the caller-owned `struct list_head` plus each `struct imapper`'s `slot`, `user`, `addr`, and `next`. Hardware persistence is delegated to `map_op`, so list changes and hardware programming stay paired.

## Dependencies and integration points

It depends on Linux list primitives and `ctimap.h`. `ctsrc.c` uses it in `srcimp_imap_add()` and `srcimp_imap_delete()` while holding `imap_lock`, with `srcimp_map_op()` programming SRC input mapper registers.

## Risks and test signals

Risks include unordered duplicates, deleting an entry not on the list, map operation failures being ignored, and wraparound mistakes corrupting the hardware chain. Useful tests allocate multiple mapper entries with sorted, tail, head, and single-entry deletion cases and verify callback order plus final `next` links.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctimap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctimap.h -->
# sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctimap.h

## Purpose

This header defines the generic input-mapper node and list operations used by ctxfi resource managers.

## Important APIs, types, and functions

`struct imapper` stores an input `slot`, consuming `user`, mapper RAM `addr`, linked-list `next`, and `list_head`. It declares `input_mapper_add()`, `input_mapper_delete()`, and `free_input_mapper_list()`.

## Control flow

Callers allocate mapper entries, maintain a list head, and supply a `map_op` callback that receives each changed entry whenever the chain is modified.

## State and persistence behavior

The header defines in-memory mapper state only. Persistent hardware state is produced by callback users such as SRCIMP manager code.

## Dependencies and integration points

It depends on `<linux/list.h>` and is included by `ctsrc.h`/`ctsrc.c` for SRC input mapper resource management.

## Risks and test signals

The structure is shared with hardware programming code, so field semantics must remain stable. Compile tests and SRCIMP mapping/unmapping tests are the best signals.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctimap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctmixer.c -->
# sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctmixer.c

## Purpose

This file builds the ctxfi internal mixer topology and exports ALSA mixer controls for volumes, capture/playback switches, IEC958 status, analog route, and model-specific output/mic controls.

## Important APIs, types, and functions

Public entry points are `ct_mixer_create()`, `ct_mixer_destroy()`, and `ct_alsa_mix_create()`. Internal enums map ALSA controls to AMIXER and SUM resources. `ct_mixer_kcontrols_create()` registers controls. `ct_mixer_topology_build()` wires AMIXER and SUM resources. `mixer_get_output_ports()`, `mixer_set_input_left()`, and `mixer_set_input_right()` are installed in `struct ct_mixer`. Volume handlers scale ALSA values by `VOL_SCALE`; switch handlers call `do_switch()`.

## Control flow

Creation allocates arrays, allocates SUM and AMIXER resources from ATC resource managers, builds a fixed stereo topology, and exposes operations. ALSA control creation loops over enabled volume and switch descriptors, adds IEC958 controls, and conditionally adds output, mic-source, and RCA route controls from hardware capabilities. Runtime switch changes update `mixer->switch_state`, rewire capture AMIXERs for selected sources, and call ATC mute/source functions.

## State and persistence behavior

The mixer persists `switch_state`, AMIXER scale/input/sum configuration, SUM resources, and ALSA kcontrols. PM resume recommits every AMIXER and reapplies each switch state. Two static `kctls` pointers cache line-in and mic switch controls for notifications, which is explicitly noted as problematic for multiple cards.

## Dependencies and integration points

It depends on `ctatc`, `ctresource`, `ctamixer`, ALSA control/TLV/PCM APIs, and hardware capability callbacks. PCM routing uses `ct_mixer` operations to connect PCM/SRC resources to mixer ports. IEC958 controls call ATC SPDIF get/set helpers.

## Risks and test signals

Risks include the global `kctls[2]` multi-card bug, mutable static control templates during registration, incomplete rollback on `snd_ctl_add()` errors, route/switch mismatches for dedicated RCA cards, and capture source conflicts. Test signals include `amixer` enumeration, volume persistence across suspend/resume, line/mic mutual exclusion notifications, SPDIF status round trips, RCA/front routing on CTOK0010, and resource leak checks after failed creation.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctmixer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctmixer.h -->
# sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctmixer.h

## Purpose

This header defines the ctxfi mixer object and its public creation/destruction API.

## Important APIs, types, and functions

`INIT_VOL` is the default hardware mixer gain. `enum MIXER_PORT_T` names logical mixer ports for wave, SPDIF, PCM, mic, and line paths. `struct ct_mixer` stores the parent ATC, AMIXER/SUM resource arrays, switch bitmap, routing callbacks, and optional PM resume callback. It declares `ct_alsa_mix_create()`, `ct_mixer_create()`, and `ct_mixer_destroy()`.

## Control flow

ATC creates a `ct_mixer`, then ALSA device setup calls `ct_alsa_mix_create()` to register controls. PCM and routing code use the callback members rather than reaching into AMIXER internals.

## State and persistence behavior

The header describes mixer-owned state but does not allocate it. The switch bitmap is the persistent software source for replaying hardware mute/source state after resume.

## Dependencies and integration points

It depends on `ctatc.h` and `ctresource.h`. It is consumed by ATC setup and PCM/routing code that needs mixer endpoints as generic `struct rsc` objects.

## Risks and test signals

Enum order is ABI-like within the driver because implementation tables depend on it. Compile coverage plus smoke tests for all exposed ALSA controls catch mismatches.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctmixer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctpcm.c -->
# sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctpcm.c

## Purpose

This file creates ALSA PCM devices for ctxfi and bridges PCM operations to ATC playback, capture, SPDIF passthrough, and timer resources.

## Important APIs, types, and functions

The public API is `ct_alsa_pcm_create()`. Static hardware descriptors define normal playback, SPDIF passthrough playback, and capture constraints. PCM callbacks include open/close, hw_params/hw_free, prepare, trigger, and pointer functions for playback and capture. `ct_atc_pcm_interrupt()` calls `snd_pcm_period_elapsed()` for timer callbacks, and `ct_atc_pcm_free_substream()` releases ATC resources plus the timer instance.

## Control flow

Open allocates `ct_atc_pcm`, selects the correct runtime hardware descriptor, applies period/buffer constraints, creates a timer instance, and stores private data. Prepare asks ATC to allocate/configure hardware resources. Trigger starts/stops ATC streams. Pointer queries ATC byte positions and converts to frames. `ct_alsa_pcm_create()` creates playback/capture counts per logical device, attaches ops, installs SG buffers, and adds channel maps.

## State and persistence behavior

Per-substream state lives in `struct ct_atc_pcm`, runtime private data, timer instance, and ATC-allocated hardware resources. IEC958 opens enable SPDIF passthrough and close disables it. PM stores PCM pointers in `atc->pcms[]` when enabled.

## Dependencies and integration points

It depends on `ctatc.h`, `cttimer.h`, ALSA PCM APIs, SG DMA allocation, and channel-map helpers. ATC implements all actual resource allocation, transport start/stop, and position reporting.

## Risks and test signals

Risks include accepting unsupported trigger commands as success, position wrap to zero when exceeding buffer size, resource leaks if prepare partially fails in ATC, SPDIF passthrough state stuck on close errors, and channel-map mismatches. Tests should open all logical PCM devices, validate constraints with `aplay`/`arecord`, exercise pause/resume/stop, verify period interrupts, and check SPDIF passthrough formats.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctpcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctpcm.h -->
# sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctpcm.h

## Purpose

This header exposes ALSA PCM creation for ctxfi logical devices.

## Important APIs, types, and functions

It includes `ctatc.h` and declares `ct_alsa_pcm_create(struct ct_atc *atc, enum CTALSADEVS device, const char *device_name)`.

## Control flow

ATC device setup calls this function for each logical PCM device it wants to register.

## State and persistence behavior

The header owns no state; PCM runtime state is allocated by `ctpcm.c` callbacks.

## Dependencies and integration points

It couples PCM registration to the ATC device enum and ALSA card stored in `struct ct_atc`.

## Risks and test signals

The main risk is enum/device mismatch with ATC callers. Build tests and ALSA PCM enumeration catch regressions.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctpcm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctresource.c -->
# sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctresource.c

## Purpose

This file implements generic bitmap resource allocation and base `struct rsc` lifecycle for ctxfi hardware resources.

## Important APIs, types, and functions

Public functions are `mgr_get_resource()`, `mgr_put_resource()`, `rsc_init()`, `rsc_uninit()`, `rsc_mgr_init()`, and `rsc_mgr_uninit()`. Internal helpers `get_resource()` and `put_resource()` manage contiguous bits. Generic `rsc_ops` expose `master`, `next_conj`, `index`, and `output_slot`.

## Control flow

Resource managers allocate a zeroed bitmap and ask the hardware backend for type-specific manager control blocks. `mgr_get_resource()` searches for contiguous free entries and decrements availability. `rsc_init()` initializes index/type/MSR/hardware pointers and obtains per-resource control blocks for SRC and AMIXER. `rsc_uninit()` returns those control blocks and clears fields. `next_conj()` advances by a rate-dependent audio-slot stride.

## State and persistence behavior

Manager state is the allocation bitmap, total/available counts, type, hardware pointer, and manager control block. Resource state is index, conjugate index, type, master sample-rate mask/count, control block, hardware pointer, and ops. Hardware programming remains in backend callbacks.

## Dependencies and integration points

It depends on `ctresource.h`, `cthardware.h`, Linux allocation, and backend vtables. SRC, SRCIMP, AMIXER, SUM, and DAIO managers build on this layer.

## Risks and test signals

Risks include bitmap bounds errors, lack of double-free detection, global assumptions about `NUM_RSCTYP`, invalid `msr` causing conjugate stride errors, and partial initialization cleanup. Tests should allocate/free contiguous blocks, exhaust resources, validate conjugate output slots by type/MSR, and run leak checks during manager failure injection.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctresource.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctresource.h -->
# sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctresource.h

## Purpose

This header defines ctxfi's generic hardware resource model and manager interface.

## Important APIs, types, and functions

`enum RSCTYP` identifies SRC, SRCIMP, AMIXER, SUM, and DAIO resources. `struct rsc` packs index, type, conjugate index, MSR, control block, hardware pointer, and ops. `struct rsc_ops` defines generic navigation and output-slot callbacks. `struct rsc_mgr` stores type, amount, availability, bitmap, control block, and hardware pointer. The header declares resource and manager init/uninit plus bitmap get/put functions.

## Control flow

Specific managers embed or contain `struct rsc_mgr`, then call these helpers to allocate resource IDs and initialize generic resource objects before adding type-specific behavior.

## State and persistence behavior

The header defines in-memory allocation and resource identity state. Hardware persistence is delegated through `struct hw` callbacks referenced by `rsc->hw` and `mgr->hw`.

## Dependencies and integration points

It depends on Linux integer types and forward-declared hardware objects. It is a shared contract for SRC, AMIXER, SUM, DAIO, mixer, and PCM routing modules.

## Risks and test signals

Bitfield widths limit indexes and types; adding resource types or larger hardware pools requires care. Compile-time structure users plus resource allocation tests provide coverage.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctresource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctsrc.c -->
# sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctsrc.c

## Purpose

This file implements Sample Rate Converter resource management and SRC input-mapper resource management for ctxfi.

## Important APIs, types, and functions

Public constructors/destructors are `src_mgr_create()`, `src_mgr_destroy()`, `srcimp_mgr_create()`, and `srcimp_mgr_destroy()`. SRC operations wrap hardware setters for state, format, buffer mode, pitch, addresses, and commit. `get_src_rsc()`/`put_src_rsc()` allocate and release SRC resources. SRCIMP operations include `srcimp_map()`, `srcimp_unmap()`, `get_srcimp_rsc()`, and `put_srcimp_rsc()`.

## Control flow

SRC creation initializes a generic resource manager, disables all 256 SRCs, and installs callbacks. A source request allocates one or more contiguous SRCs for interleaved memory-read mode or one SRC for write/ring modes, configures defaults, enables all conjugates, and commits manager state. Commits program the master resource and relevant conjugates. SRCIMP creation seeds the mapper list with a zero entry; mapping allocates per-MSR imapper entries and uses `ctimap` to maintain a sorted circular chain that is written to hardware through `srcimp_map_op()`.

## State and persistence behavior

SRC manager state includes bitmap allocation, manager control block, spinlock, card pointer, and global `conj_mask` derived from hardware. Each `struct src` stores mode, multi count, interleave link, and generic resource state. SRCIMP state includes allocated indexes per conjugate, mapper entries, mapped bitmask, manager pointer, and a shared mapper list protected by `imap_lock`.

## Dependencies and integration points

It depends on `ctsrc.h`, `cthardware.h`, `ctresource.c`, and `ctimap.c`. ATC and PCM preparation use SRC resources for host-memory reads/writes and audio-ring routing. Mixer/routing code consumes SRC output slots and SRCIMP mappings.

## Risks and test signals

Risks include the file-scope `conj_mask` being shared across devices, error unwinding with partially allocated SRCIMP indexes, MEMRD interleave allocation assumptions, ignored mapper callback errors, and incorrect conjugate programming for high sample-rate multiples. Tests should exercise playback/capture resource allocation at MSR 1/2/4, SRCIMP map/unmap ordering, resource exhaustion, and suspend/resume reconfiguration.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctsrc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctsrc.h -->
# sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctsrc.h

## Purpose

This header defines SRC and SRCIMP resource objects, descriptors, operations, states, and manager constructors.

## Important APIs, types, and functions

It defines SRC states (`OFF`, `INIT`, `RUN`), sample formats, `enum SRCMODE`, `struct src`, `struct src_rsc_ops`, `struct src_desc`, `struct src_mgr`, `struct srcimp`, `struct srcimp_rsc_ops`, `struct srcimp_desc`, and `struct srcimp_mgr`. It declares `src_mgr_create/destroy()` and `srcimp_mgr_create/destroy()`.

## Control flow

Callers request resources through manager callback members, then use per-resource ops to configure and commit hardware. SRCIMP users map an input resource to a SRC user and later unmap it.

## State and persistence behavior

The header defines per-resource mode, interleaving, mapped-bit, mapper-list, and locking state. Persistence to hardware is performed through backend callbacks and mapper writes in `ctsrc.c`.

## Dependencies and integration points

It depends on `ctresource.h`, `ctimap.h`, Linux spinlocks/lists, and ALSA core card types. It is consumed by ATC stream setup and routing code.

## Risks and test signals

The manager APIs depend on correct lock usage and resource lifecycle ownership. Compile coverage plus stream setup/teardown tests across playback, capture, and ring modes are the best signals.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctsrc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/cttimer.c -->
# sources/distributed-fs/ceph-client/sound/pci/ctxfi/cttimer.c

## Purpose

This file provides per-PCM period notification timing for ctxfi using either Linux system timers or the native X-Fi interval timer IRQ.

## Important APIs, types, and functions

Public APIs are `ct_timer_new()`, `ct_timer_free()`, `ct_timer_instance_new()`, `ct_timer_instance_free()`, `ct_timer_prepare()`, `ct_timer_start()`, and `ct_timer_stop()`. Internal `struct ct_timer_instance` tracks one PCM stream; `struct ct_timer` manages global lists and native timer state. `ct_systimer_ops` implements per-stream `timer_list` scheduling. `ct_xfitimer_ops` multiplexes native timer IRQs across running streams.

## Control flow

`ct_timer_new()` selects native timer unless `use_system_timer` is set or hardware lacks timer IRQ support; native mode installs an IRQ callback in `struct hw`. Each PCM open creates an instance. System timer mode schedules the next callback from period size, current pointer, and sample rate. Native mode keeps a running list, reads hardware wallclock, computes the nearest fragment deadline, rearms the hardware timer, and calls `snd_pcm_period_elapsed()` outside the global timer lock when needed.

## State and persistence behavior

State includes per-instance running flags, last position, fragment countdown, need-update flag, and list membership. Global state includes instance/running lists, wallclock baseline, IRQ-handling/reprogram flags, and whether the hardware timer is running. State is in memory only, but native mode also persists timer enable/tick values in hardware registers.

## Dependencies and integration points

It depends on module parameter handling, ALSA PCM/core, `ctatc`, and `cthardware` timer callbacks. `ctpcm.c` creates one timer instance per substream and calls prepare/start/stop from PCM lifecycle paths.

## Risks and test signals

Risks include list races between IRQ and close, timer delete semantics in system mode, period calculation drift at unusual rates/formats, native timer reprogram races, and callbacks after `ct_timer_free()`. Tests should force both timer modes, run concurrent playback/capture streams, stress pause/resume/close, and verify stable period interrupts without XRUNs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/cttimer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/cttimer.h -->
# sources/distributed-fs/ceph-client/sound/pci/ctxfi/cttimer.h

## Purpose

This header declares the ctxfi PCM timer manager and timer-instance lifecycle API.

## Important APIs, types, and functions

It forward declares `struct ct_timer` and `struct ct_timer_instance`, plus constructors/destructors and prepare/start/stop functions for timer instances.

## Control flow

PCM open calls `ct_timer_instance_new()`, prepare/start/stop call the matching functions, and runtime private cleanup calls `ct_timer_instance_free()`. ATC-level setup owns `ct_timer_new()` and `ct_timer_free()`.

## State and persistence behavior

The header exposes opaque timer objects; all state lives in `cttimer.c`.

## Dependencies and integration points

It depends on Linux spinlock/timer/list declarations only for surrounding type compatibility and is included by `ctpcm.c`.

## Risks and test signals

The opaque API reduces direct misuse, but callers must free instances before the global timer. PCM lifecycle tests and module unload tests catch ordering bugs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/cttimer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctvmem.c -->
# sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctvmem.c

## Purpose

This file implements the device virtual-memory allocator and page-table population used by ctxfi transport DMA.

## Important APIs, types, and functions

Public APIs are `ct_vm_create()` and `ct_vm_destroy()`. The `ct_vm` object installs `map`, `unmap`, and `get_ptp_phys` callbacks implemented by `ct_vm_map()`, `ct_vm_unmap()`, and `ct_get_ptp_phys()`. Internal `get_vm_block()` and `put_vm_block()` allocate and merge logical address blocks.

## Control flow

Creation allocates page-table pages, initializes unused/used block lists with one free block spanning the virtual address space, and returns callbacks. Mapping finds a page-aligned free block, moves or splits it into the used list, then fills page table entries from `snd_pcm_sgbuf_get_addr()`. Unmapping returns the block to the free list and coalesces neighbors. Destroy frees all list nodes and DMA page-table pages.

## State and persistence behavior

Persistent state is the page-table DMA buffer, logical address-space size, used/unused block lists, and mutex. Hardware sees the page-table physical address through `ct_get_ptp_phys()` and `hw_trn_init()` in the hardware backend. Individual blocks retain original requested size after page-table population.

## Dependencies and integration points

It depends on `ctvmem.h`, `ctatc.h`, ALSA PCM SG buffers, ALSA DMA allocation, and PCI devices. ATC stream preparation maps PCM buffers into this virtual space before transport setup.

## Risks and test signals

Risks include using `CT_PAGE_MASK` based on `PAGE_SIZE` rather than `CT_PAGE_SIZE`, silent failure when initial free block allocation fails, page-table bounds mistakes for large buffers, and lack of hardware TLB invalidation on unmap. Tests should map/unmap varied buffer sizes, check coalescing, validate page-table entries for SG buffers, and run playback/capture after repeated hw_params changes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctvmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctvmem.h -->
# sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctvmem.h

## Purpose

This header defines ctxfi device virtual-memory structures for mapping host PCM buffers into the card's logical address space.

## Important APIs, types, and functions

It defines `CT_PTP_NUM`, `CT_PAGE_SIZE`, `CT_PAGE_SHIFT`, alignment macros, `struct ct_vm_block`, and `struct ct_vm`. `struct ct_vm` owns page-table DMA buffers, used/free lists, a mutex, and `map`, `unmap`, and `get_ptp_phys` callbacks. It declares `ct_vm_create()` and `ct_vm_destroy()`.

## Control flow

ATC creates a VM object during hardware setup, maps substream buffers during PCM preparation, and supplies the page-table physical address to hardware initialization.

## State and persistence behavior

The defined state persists for the card lifetime and for each mapped PCM buffer. Hardware consumes the page-table pages while transport is active.

## Dependencies and integration points

It depends on Linux mutex/list/PCI APIs and ALSA memalloc. It is integrated with `cthw20k2.c` transport setup and ATC PCM resource management.

## Risks and test signals

Page-size assumptions and map/unmap ordering are the main risks. Build tests plus repeated SG buffer mapping under playback/capture load give the strongest signal.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctvmem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/xfi.c -->
# sources/distributed-fs/ceph-client/sound/pci/ctxfi/xfi.c

## Purpose

This is the PCI module entry point for Creative X-Fi ctxfi cards. It matches Creative 20K1/20K2 devices, creates ALSA cards, delegates hardware/ATC setup, registers ALSA devices, and wires PM callbacks.

## Important APIs, types, and functions

Static module parameters include `reference_rate`, `multiple`, `index`, `id`, `enable`, and `subsystem`. `ct_pci_dev_ids` maps PCI IDs to `ATC20K1`/`ATC20K2`. `ct_card_probe()` creates and registers the card. `ct_card_remove()` frees it. `ct_card_suspend()` and `ct_card_resume()` delegate to ATC when PM is enabled. `ct_driver` is registered through `module_pci_driver()`.

## Control flow

Probe checks the global card slot, honors `enable[]`, creates `snd_card`, validates module parameters, calls `ct_atc_create()`, creates ALSA devices through `ct_atc_create_alsa_devs()`, fills card names, registers the card, stores drvdata, and increments the static device counter. Error paths free the card. Remove frees drvdata. PM retrieves `ct_atc` from card private data.

## State and persistence behavior

State includes module parameters, a static probe counter, ALSA card private data, PCI drvdata, and ATC-managed hardware state. No persistent user configuration is stored beyond module parameters.

## Dependencies and integration points

It depends on Linux PCI/module APIs, ALSA card initialization, `ctatc.h`, and `cthardware.h`. It is the parent integration point for all ctxfi PCM, mixer, timer, resource, and hardware backend modules.

## Risks and test signals

Risks include the static `dev` counter not being decremented on remove, global mutation of invalid module parameters, subsystem override misuse, and PM callback assumptions about drvdata. Test signals include module load/unload, multi-card probing, invalid parameter fallback messages, suspend/resume, and correct ALSA card naming for 20K1 and 20K2 devices.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/xfi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/Makefile -->
# sources/distributed-fs/ceph-client/sound/pci/echoaudio/Makefile

## Purpose

This Makefile declares the ALSA Echoaudio PCI card modules and maps Kconfig symbols to object targets.

## Important APIs, types, and functions

It defines one `snd-*-y` composite object per supported card family member, including Darla20, Darla24, Echo3G, Gina, Layla, Mona, Mia, and Indigo variants. `obj-$(CONFIG_SND_...)` lines add enabled modules to the build.

## Control flow

Kernel kbuild evaluates each `CONFIG_SND_*` symbol and builds the matching single-object module. Each card `.c` file includes shared implementation files rather than linking separate shared objects.

## State and persistence behavior

The Makefile stores build-time module composition only; it has no runtime state.

## Dependencies and integration points

It integrates Echoaudio card drivers into the ALSA PCI sound build and depends on Kconfig symbols from the surrounding sound subsystem.

## Risks and test signals

Risks are missing object mappings, stale card names, or build symbol drift. Test signals are allmodconfig/build coverage and module presence for each selected `CONFIG_SND_*`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/darla20.c -->
# sources/distributed-fs/ceph-client/sound/pci/echoaudio/darla20.c

## Purpose

This card wrapper specializes the shared Echoaudio driver for Darla20.

## Important APIs, types, and functions

It defines feature macros `ECHOGALS_FAMILY`, `ECHOCARD_DARLA20`, `ECHOCARD_NAME`, and `ECHOCARD_HAS_MONITOR`; pipe and bus indexes for 8 analog outs and 2 analog ins; `MODULE_FIRMWARE("ea/darla20_dsp.fw")`; firmware table `card_fw`; PCI IDs for subsystem `0x0010`; and `pcm_hardware_skel` for 44.1/48 kHz, up to stereo streams. It includes `darla20_dsp.c`, `echoaudio_dsp.c`, and `echoaudio.c`.

## Control flow

Compilation textually combines card constants, Darla20 DSP policy, generic DSP helpers, and the shared ALSA PCI driver. Probe in `echoaudio.c` uses the local PCI table and calls `init_hw()` from `darla20_dsp.c`.

## State and persistence behavior

Runtime state is the shared `struct echoaudio`; this wrapper fixes channel layout, supported formats/rates, monitor support, and firmware selection.

## Dependencies and integration points

It depends on ALSA, PCI, firmware loading, `echoaudio.h`, and the included shared implementation files. Kbuild creates `snd-darla20.o` from this unit.

## Risks and test signals

Risks include macro layout mismatches, firmware name/path errors, and constraint mismatch with hardware. Test signals include successful probe with Darla20 subsystem ID, firmware load, analog PCM enumeration, monitor controls, and 44.1/48 kHz playback/capture.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/darla20.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/darla20_dsp.c -->
# sources/distributed-fs/ceph-client/sound/pci/echoaudio/darla20_dsp.c

## Purpose

This file provides Darla20-specific DSP initialization and clock/sample-rate behavior for the shared Echoaudio driver.

## Important APIs, types, and functions

`init_hw()` validates the subsystem family, initializes the DSP communication page, sets firmware index `FW_DARLA20_DSP`, initializes SPDIF/clock cached state, marks ASIC loaded because none exists, sets internal-only clock support, loads firmware, and clears `bad_board`. `set_mixer_defaults()` calls `init_line_levels()`. `detect_input_clocks()` returns internal only. `load_asic()` is a no-op. `set_sample_rate()` maps 44.1/48 kHz to Darla20 DSP clock/SPDIF states and sends `DSP_VC_SET_GD_AUDIO_STATE`.

## Control flow

The shared probe calls `init_hw()`, then mixer defaults. Rate changes wait for DSP handshake, update comm-page fields, update cached clock/SPDIF state only when changed, clear handshake, and send a DSP vector.

## State and persistence behavior

State persists in `chip->device_id`, `subdevice_id`, `bad_board`, `dsp_code_to_load`, `spdif_status`, `clock_state`, `asic_loaded`, `input_clock_types`, `sample_rate`, and comm-page audio-state fields.

## Dependencies and integration points

It relies on constants and helpers from `echoaudio.h` and `echoaudio_dsp.c`, including `init_dsp_comm_page()`, `load_firmware()`, `wait_handshake()`, `clear_handshake()`, and `send_vector()`.

## Risks and test signals

Risks include unsupported rates silently using no-change DSP states, handshake failures, and stale cached clock/SPDIF state. Tests should cover firmware load, set rate to 44100 and 48000, reject wrong subsystem IDs, and verify no ASIC load is attempted.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/darla20_dsp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/darla24.c -->
# sources/distributed-fs/ceph-client/sound/pci/echoaudio/darla24.c

## Purpose

This card wrapper specializes the shared Echoaudio driver for Darla24.

## Important APIs, types, and functions

It defines Darla24 feature macros for monitor, input/output nominal levels, external ESync clock, and super interleave. Pipe/bus layout is 8 analog outs and 2 analog ins. Firmware is `ea/darla24_dsp.fw`; PCI IDs cover subsystem `0x0040` and `0x0041`; `pcm_hardware_skel` supports 8 kHz through 96 kHz, up to 8 playback channels.

## Control flow

Like other Echoaudio wrappers, this file is a compile unit that includes `darla24_dsp.c`, `echoaudio_dsp.c`, and `echoaudio.c`. The shared probe uses its local firmware table, PCI IDs, PCM skeleton, and feature macros.

## State and persistence behavior

The wrapper fixes static runtime capabilities: no ASIC, monitor mixer, nominal-level controls, ESync external clock list, super-interleaved hardware behavior, and PCM constraints.

## Dependencies and integration points

It depends on ALSA/PCI/firmware APIs and `echoaudio.h`. Kbuild maps `CONFIG_SND_DARLA24` to this module.

## Risks and test signals

Risks include rate/channel constraints that do not match DSP firmware, missing nominal-level controls, and ESync detection drift. Tests should probe both revisions, enumerate analog PCM and controls, switch internal/ESync clock, and run 8/44.1/48/88.2/96 kHz streams.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/darla24.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/darla24_dsp.c -->
# sources/distributed-fs/ceph-client/sound/pci/echoaudio/darla24_dsp.c

## Purpose

This file implements Darla24-specific DSP initialization, external clock detection, sample-rate programming, and input-clock selection.

## Important APIs, types, and functions

`init_hw()` validates Darla24 subsystem IDs, initializes the comm page, selects firmware `FW_DARLA24_DSP`, marks no-ASIC loaded, advertises internal and ESync clocks, loads firmware, and clears `bad_board`. `detect_input_clocks()` maps DSP `GLDM_CLOCK_DETECT_BIT_ESYNC` to `ECHO_CLOCK_BIT_ESYNC`. `set_sample_rate()` maps supported rates to GD24 clock codes and uses `GD24_EXT_SYNC` when ESync is selected. `set_input_clock()` accepts internal or ESync and reapplies the current sample rate.

## Control flow

Firmware load happens during shared probe. Runtime rate or clock changes update `chip->sample_rate`, comm-page `sample_rate` and `gd_clock_state`, then clear the handshake and send `DSP_VC_SET_GD_AUDIO_STATE`.

## State and persistence behavior

Persistent state includes current `sample_rate`, `input_clock`, `input_clock_types`, firmware index, `asic_loaded`, and comm-page clock fields. ESync mode overrides the clock code while keeping the requested sample rate in software.

## Dependencies and integration points

It uses `echoaudio.h` constants and shared DSP helpers. Shared ALSA clock-source controls call `set_input_clock()` and channel-info controls call `detect_input_clocks()`.

## Risks and test signals

Risks include invalid clock-source acceptance, race with open PCM streams through shared controls, incorrect ESync detect mapping, and unsupported rate rejection. Tests should change every supported rate, toggle ESync with and without detected clock, and verify controls report valid clock masks.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/darla24_dsp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/echo3g.c -->
# sources/distributed-fs/ceph-client/sound/pci/echoaudio/echo3g.c

## Purpose

This wrapper specializes the shared Echoaudio driver for Echo3G-family PCI cards with external Gina3G/Layla3G boxes.

## Important APIs, types, and functions

It defines Echo3G feature macros for ASIC, monitor, nominal levels, super interleave, digital I/O, digital mode switch, ADAT, external clock, stereo big-endian 32-bit support, MIDI, and phantom power. Pipe and bus indexes are dynamic `chip->px_*`/`chip->bx_*` fields populated after box detection. Firmware entries are loader DSP, Echo3G DSP, and 3G ASIC. PCI ID matches device `0x3410`, subsystem `0x0100`. `pcm_hardware_skel` supports 32 kHz through continuous up to 100 kHz.

## Control flow

The file includes `echo3g_dsp.c`, generic DSP helpers, `echoaudio_3g.c`, shared `echoaudio.c`, and MIDI support. During probe, `init_hw()` loads firmware/ASIC, detects the external box type, and sets dynamic channel counts before shared PCM/control registration.

## State and persistence behavior

The wrapper enables dynamic runtime state for box-dependent pipe/bus layout, digital modes, MIDI, phantom power availability, and clock sources. Shared `struct echoaudio` stores those values.

## Dependencies and integration points

It depends on firmware files under `ea/`, ALSA rawmidi, PCI, firmware, and the generic Echoaudio include-based architecture. Kbuild maps `CONFIG_SND_ECHO3G` to this unit.

## Risks and test signals

Risks include missing firmware, failed ASIC load, wrong external box detection, dynamic channel counts set too late, and feature controls shown for unsupported boxes. Tests should probe Gina3G and Layla3G boxes, validate analog/digital PCM counts, ADAT/SPDIF modes, MIDI, phantom power only on Gina3G, firmware cache behavior, and suspend/resume.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/echo3g.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/echo3g_dsp.c -->
# sources/distributed-fs/ceph-client/sound/pci/echoaudio/echo3g_dsp.c

## Purpose

This file provides Echo3G card-specific DSP initialization, external-box classification, mixer defaults, and phantom-power control hooks.

## Important APIs, types, and functions

`init_hw()` initializes the comm page, seeds the 48 kHz frequency register, sets firmware `FW_ECHO3G_DSP`, enables MIDI, loads firmware/ASIC, interprets returned box type as Gina3G or Layla3G, fills clock masks, card name, pipe/bus indexes, and box capabilities, then advertises SPDIF RCA/optical/ADAT modes. `set_mixer_defaults()` sets default digital/SPDIF/phantom state and initializes line levels. `set_phantom_power()` toggles `E3G_PHANTOM_POWER` through `write_control_reg()`.

## Control flow

The shared probe calls `init_hw()`. Firmware loading returns a box type from `load_asic()` in `echoaudio_3g.c`; the result controls subsequent channel layout. Phantom-power ALSA control calls `set_phantom_power()` only when `chip->has_phantom_power` is true.

## State and persistence behavior

State persists in comm-page control/frequency registers, `card_name`, dynamic pipe/bus indexes, `input_clock_types`, `digital_modes`, `has_phantom_power`, `hasnt_input_nominal_level`, `phantom_power`, `bad_board`, and `has_midi`.

## Dependencies and integration points

It forward-declares helpers implemented in `echoaudio_3g.c`, uses shared DSP helpers, and is textually included by `echo3g.c` before the shared driver.

## Risks and test signals

Risks include `local_irq_enable()` during init, misclassification of external boxes, partially initialized dynamic indexes on errors, and phantom-power control writes racing with other control-register updates. Tests should cover both box types, missing box, firmware failure, phantom-power toggling, MIDI availability, and control registration differences.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/echo3g_dsp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/echoaudio.c -->
# sources/distributed-fs/ceph-client/sound/pci/echoaudio/echoaudio.c

## Purpose

This is the shared ALSA PCI driver implementation included by each Echoaudio card wrapper. It handles firmware caching, PCM devices, controls, IRQs, probe/create/free, and suspend/resume using card-specific macros and DSP functions supplied by the including file.

## Important APIs, types, and functions

Major groups are firmware helpers (`get_firmware()`, `free_firmware_cache()`), PCM callbacks (`pcm_open()`, `init_engine()`, `pcm_prepare()`, `pcm_trigger()`, `pcm_pointer()`), control handlers for output/input gain, nominal levels, monitor/vmixer, digital mode, SPDIF mode, clock source, phantom power, automute, VU meters, and channel info, IRQ handler `snd_echo_interrupt()`, creation functions `snd_echo_create()` and `__snd_echo_probe()`, and PM callbacks `snd_echo_suspend()`/`snd_echo_resume()`. The PCI driver is registered as `echo_driver`.

## Control flow

Probe creates a managed ALSA card with `struct echoaudio`, maps DSP registers, requests IRQ, allocates the DSP comm page, calls card-specific `init_hw()` and `set_mixer_defaults()`, then registers PCM, MIDI if enabled, controls based on feature macros and runtime capability flags, and the ALSA card. PCM open installs constraints and SG-list memory; hw_params allocates pipes, builds DSP SG instructions, sets the global sample rate, and stores the substream. Prepare sets audio format. Trigger starts/stops/pauses transport for grouped substreams. IRQ service calls card DSP service code, checks every running substream for period advancement, and forwards MIDI input.

## State and persistence behavior

Persistent state is `struct echoaudio`: locks, mode mutex, open-count/rate gating, PCM/MIDI handles, firmware cache, DSP register mapping, comm page, pipe allocation/cyclic masks, sample rate, digital mode, clock source, gains, monitor/vmixer matrices, nominal levels, meter state, ASIC/firmware status, and optional MIDI/3G fields. Firmware entries are cached until card free. Suspend sends the DSP comatose vector, frees IRQ, clears DSP code; resume reloads hardware, restores DSP settings, restores selected comm-page arrays, and re-requests IRQ.

## Dependencies and integration points

It depends on the including card file for `ECHOCARD_*` macros, `snd_echo_ids`, `card_fw`, `pcm_hardware_skel`, and card-specific DSP functions. It uses ALSA core/PCM/control/rawmidi APIs, PCI managed resources, firmware loader, DSP helper functions from `echoaudio_dsp.c`, optional `midi.c`, and optional 3G helpers.

## Risks and test signals

Risks include include-based compile-unit coupling, global sample-rate policy across open streams, lock ordering between `mode_mutex` and spinlocks, period detection without hardware source IDs, firmware cache lifetime, suspend/resume restoration gaps, and many feature-macro paths that compile only for some cards. Test signals include all selected card modules building, probe/remove, firmware load and cache release, PCM constraints for analog/digital paths, grouped trigger behavior, mixer control get/put, VU meters, MIDI IRQ path, PM resume with previous mixer/format settings, and race testing while opening streams and changing digital/clock modes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/echoaudio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/echoaudio.h -->
# sources/distributed-fs/ceph-client/sound/pci/echoaudio/echoaudio.h

## Purpose

This header is the shared Echoaudio driver contract. It documents the pipe/bus model, defines common constants, state structures, helper declarations, and inline channel-layout accessors used by all Echoaudio card wrappers.

## Important APIs, types, and functions

It defines PCI IDs, subsystem IDs, max channel/pipe/MIDI sizes, clock constants and bitmasks, digital mode constants/capability masks, gain limits, pipe states, `struct audiopipe`, `struct audioformat`, and the large `struct echoaudio`. It declares shared DSP helper entry points and optional MIDI hooks. Inline helpers wrap DSP register reads/writes, handshake clearing, pipe/bus index macros, channel counts, and monitor matrix indexing.

## Control flow

Each card wrapper defines `PX_*`, `BX_*`, and feature macros before including this header. Shared code then uses the inline helpers to compute PCM counts, control counts, and bus/pipe offsets without knowing whether values are constants or dynamic 3G fields.

## State and persistence behavior

`struct echoaudio` is the persistent per-card state for the whole shared driver: synchronization, ALSA objects, PCI/MMIO/IRQ resources, comm page, pipe masks, sample rate, digital/clock settings, firmware/ASIC state, gains, monitor/vmixer matrices, nominal levels, firmware cache, MIDI state, and Echo3G dynamic channel layout.

## Dependencies and integration points

It depends on `echoaudio_dsp.h`, ALSA core/PCM/DMA types through included sources, and card-defined macros. It is included by every Echoaudio card module and by shared implementation files.

## Risks and test signals

Risks include macro-order dependency, dynamic-vs-static pipe index confusion, oversized shared state changes affecting all card modules, and comment/API drift from the DSP helpers. Test signals include building multiple card wrappers, verifying channel counts for Darla20/Darla24/Echo3G, and exercising controls that index gain matrices.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/echoaudio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/echoaudio_3g.c -->
# sources/distributed-fs/ceph-client/sound/pci/echoaudio/echoaudio_3g.c

## Purpose

This file contains common low-level control logic for Echoaudio 3G cards, especially ASIC loading, external clock detection, digital mode switching, sample-rate programming, SPDIF flags, and input clock selection.

## Important APIs, types, and functions

Key functions are `check_asic_status()`, `get_frq_reg()`, `write_control_reg()`, `set_digital_mode()`, `set_spdif_bits()`, `set_professional_spdif()`, `detect_input_clocks()`, `load_asic()`, `set_sample_rate()`, `set_input_clock()`, and `dsp_set_digital_mode()`.

## Control flow

ASIC load sends the generic 3G ASIC firmware, waits for hardware settle, tests ASIC status, and writes the default 48 kHz internal/SPDIF RCA control state. Control-register updates wait for DSP handshake, compare desired little-endian comm-page values, update only on change or force, clear handshake, and send `DSP_VC_WRITE_CONTROL_REG`. Sample-rate and input-clock changes manipulate control bits and frequency register depending on internal, SPDIF, ADAT, or word-clock mode. Digital-mode changes reject incompatible active pipes, switch incompatible clocks to internal, update control bits, then refresh monitor/gain state when ADAT changes channel meaning.

## State and persistence behavior

Persistent state includes `asic_loaded`, `asic_code`, `digital_mode`, `input_clock`, `sample_rate`, `professional_spdif`, `non_audio_spdif`, comm-page `control_register`, `e3g_frq_register`, `status_clocks`, and gain/meter state refreshed through shared helpers.

## Dependencies and integration points

It depends on DSP vectors, 3G constants from `echoaudio_dsp.h`, shared helper functions from `echoaudio_dsp.c`, and ALSA controls in `echoaudio.c` that call digital, SPDIF, clock, and channel-info functions.

## Risks and test signals

Risks include control-register lost updates under concurrent controls, ADAT rejecting high sample rates, incorrect detection masks for SPDIF96/WORD96, one-second ASIC load delay affecting probe latency, and failure to refresh gains after channel-count mode changes. Tests should switch RCA/optical/ADAT modes, try incompatible clocks, test continuous rates, verify SPDIF professional/non-audio bits, load ASIC from cold boot, and read channel-info clock masks with different external clocks connected.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/echoaudio_3g.c -->
