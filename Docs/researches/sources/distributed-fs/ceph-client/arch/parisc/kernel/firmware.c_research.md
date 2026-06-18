# sources/distributed-fs/ceph-client/arch/parisc/kernel/firmware.c

## Purpose

`firmware.c` is the PA-RISC Processor Dependent Code (PDC) access layer. It serializes firmware calls, hides 32-bit versus 64-bit firmware calling width, provides wrappers for model, memory, device, PCI, stable storage, TOD, reset, console IODC, and PAT services, and exports selected helpers to drivers. The file is central to boot-time discovery, runtime firmware services, panic paths, and legacy console I/O.

## Important APIs, Types, And Functions

The shared state is `pdc_lock`, `pdc_result[]`, and `pdc_result2[]`. Almost every wrapper holds `pdc_lock` while calling `mem_pdc_call()` and while consuming the static buffers. On 64-bit kernels `parisc_narrow_firmware` tracks whether MEM_PDC must be called through `real32_call()` or `real64_call()`.

Width conversion is handled by `set_firmware_width_unlocked()`, `set_firmware_width()`, `convert_to_wide()`, and `f_extend()`. These are required because narrow firmware returns 32-bit values that may need widening or sign extension into kernel addresses.

Discovery and model wrappers include `pdc_system_map_find_mods()`, `pdc_system_map_find_addrs()`, `pdc_model_info()`, `pdc_model_sysmodel()`, `pdc_model_versions()`, `pdc_model_cpuid()`, `pdc_model_capabilities()`, `pdc_cache_info()`, `pdc_spaceid_bits()`, `pdc_btlb_info()`, `pdc_mem_map_hpa()`, and `pdc_mem_mem_table()`.

Device and platform wrappers include `pdc_iodc_read()`, `pdc_lan_station_id()`, `pdc_get_initiator()`, `pdc_pci_irt_size()`, `pdc_pci_irt()`, `pdc_tod_read()`, `pdc_tod_set()`, `pdc_soft_power_info()`, `pdc_soft_power_button()`, `pdc_soft_power_button_panic()`, `pdc_io_reset()`, and `pdc_io_reset_devices()`.

Persistent firmware state APIs include `pdc_stable_read()`, `pdc_stable_write()`, `pdc_stable_get_size()`, `pdc_stable_verify_contents()`, and `pdc_stable_initialize()`. PAT-only 64-bit APIs include `pdc_pat_cell_get_number()`, `pdc_pat_cell_module()`, `pdc_pat_cell_info()`, `pdc_pat_cpu_get_number()`, `pdc_pat_get_irt_size()`, `pdc_pat_get_irt()`, `pdc_pat_pd_get_addr_map()`, `pdc_pat_pd_get_pdc_revisions()`, `pdc_pat_pd_get_platform_counter()`, PAT PCI config helpers, and PAT memory PDT helpers.

Low-level call marshalling is done by `real32_call()` and, for 64-bit builds, `real64_call()`. They populate architecture-specific real-mode stack overlays before entering assembly helpers.

## Control Flow

Normal wrappers follow a common pattern: acquire `pdc_lock`, prepare an aligned physical-address argument or copy caller input into `pdc_result2`, call `mem_pdc_call()` or `real32_call()`, optionally widen returned words, copy results out to caller buffers, release the lock, and return the PDC status. Some functions intentionally preset result words before calls so unsupported firmware leaves deterministic output.

The firmware-width path starts narrow on 64-bit kernels, calls `PDC_MODEL_CAPABILITIES`, and clears `parisc_narrow_firmware` when the result reports wide firmware. All later `mem_pdc_call()` invocations route through the selected real-mode call.

`pdc_iodc_print()` is a special console path. It uses a locked static page-aligned buffer, translates the first newline it emits to CRLF, and calls the boot console IODC entry through `real32_call()` regardless of OS width. `pdc_iodc_getc()` similarly uses the keyboard IODC entry if present.

Reset and emergency paths deliberately diverge from the ordinary model. `pdc_emergency_unlock()` drops the lock during stack dumping if firmware access is needed. `pdc_soft_power_button_panic()` uses `spin_trylock_irqsave()` to avoid deadlock during panic notification.

## State And Persistence Behavior

Most state is transient and protected by `pdc_lock`, but the file can read and write persistent firmware-backed stable storage through the `pdc_stable_*` API and can alter power-button policy through `pdc_soft_power_button()`. `pdc_stable_initialize()` is destructive by design. `parisc_narrow_firmware` is boot-initialized and marked `__ro_after_init`, so width selection becomes a stable global after initialization.

## Dependencies And Integration Points

This file integrates with page-zero firmware fields (`PAGE0`), real-mode assembly call helpers, PA-RISC PDC/PAT headers, boot CPU data, platform inventory, interrupt routing, SCSI and network drivers, STI console code, power management, panic notifiers, and memory-error/PDT handling. Several symbols are exported for modules or drivers, including address validation, IODC reads, LAN station IDs, stable storage, TOD, and STI calls.

## Risks

The main correctness risk is misuse of the static result buffers outside `pdc_lock`; a new wrapper that copies results after unlocking can race. Narrow-firmware widening is another high-risk area because missed `convert_to_wide()` or `f_extend()` calls can truncate firmware addresses on 64-bit kernels. Several wrappers trust caller-provided counts and PDC-reported byte counts, so buffer sizing must match the firmware contract. Panic and HPMC contexts are sensitive to lock recursion. Real-mode call marshalling has fixed argument counts and depends on external assembly stack layout.

## Test Signals

Useful signals are successful boot on narrow and wide firmware machines, correct `setup_pdc()` detection, stable `/proc/cpuinfo` and model names, device discovery through PAT and SYSTEM_MAP, functioning early IODC console output/input, successful stable-storage read/write utilities, working TOD read/set, PCI interrupt routing table discovery, and absence of lockdep or panic-path deadlocks around PDC calls.
