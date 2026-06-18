
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/note.S

Purpose: emits a PowerPC-specific ELF note advertising kernel binary capabilities to bootloaders and userland, currently the ultravisor-capable bit for PowerNV builds.

Important APIs/types/functions: `PPCCAP_ULTRAVISOR_BIT`; `PPC_CAPABILITIES_BITMAP`; `ELFNOTE(PowerPC, PPC_ELFNOTE_CAPABILITIES, ...)`.

Control flow: at assembly time, the ultravisor capability bit is set only when `CONFIG_PPC_POWERNV` is enabled; otherwise the bitmap is zero. The `ELFNOTE` macro places the capability bitmap into the kernel image's note section.

State and persistence: persistent build artifact metadata in the kernel ELF image; no runtime mutable state.

Dependencies and integration: consumed by bootloaders, tooling, or userland that inspect PowerPC ELF notes; tied to ultravisor-aware PowerNV boot requirements and `asm/elfnote.h` constants.

Risks: if the capability bit is missing on an ultravisor-capable kernel, a bootloader may refuse or warn; if set incorrectly, early boot may crash when ultravisor-controlled resources are accessed unsafely.

Test signals: inspect built kernel notes with `readelf -n`, compare PowerNV and non-PowerNV configs, and boot on ultravisor-enabled firmware.
