# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/falcon.h

Purpose: declares Falcon register offsets/bitfields, firmware image metadata structures, runtime firmware storage, and the public helper API consumed by Tegra engines with Falcon microcontrollers.

Important APIs/types: register macros cover method submission, interrupt masks/destinations, interface enable, CPU boot vector/control, DMA control/base/offset/command, and DMA transfer flags. `struct falcon_fw_bin_header_v1`, `struct falcon_fw_os_header_v1`, and section descriptors model the firmware container parsed by `falcon.c`. `struct falcon_firmware` stores the requested firmware pointer, DMA-visible virtual/physical/IOVA addresses, image size, and parsed code/data/bin sections. `struct falcon` binds device, MMIO base, and firmware state. Public functions are `falcon_init()`, `falcon_exit()`, `falcon_read_firmware()`, `falcon_load_firmware()`, `falcon_boot()`, `falcon_execute_method()`, and `falcon_wait_idle()`.

Control flow and state: the header makes allocation ownership explicit by keeping raw firmware and DMA buffer fields separate. Clients are expected to fill `dev`, `regs`, and DMA memory fields around the helper calls.

Dependencies/integration: only includes Linux integer types directly, but exposed structs use firmware, device, DMA, and `__iomem` types available through including C files. It is included by Falcon-based engine drivers and the helper implementation.

Risks: this header exposes hardware constants without type safety, so incorrect offsets or DMA context choices are compile-clean but hardware-visible. Firmware section fields are `unsigned long`/`size_t` after parsing, while hardware commands use narrower registers.

Test signals: compile coverage from NVDEC/NVJPG drivers, firmware load/boot smoke tests, and register trace validation are the practical signals.
