# sources/distributed-fs/ceph-client/arch/parisc/include/asm/pdc_chassis.h

Purpose: defines PDC chassis status, warning, LED, and display interfaces for PA-RISC systems.

Important APIs/types/functions: includes chassis message constants, LCD/LED structures, status enums, and function declarations for warning, display, and chassis log interactions.

Control flow: platform or panic paths call PDC chassis services to report boot state, warnings, panic codes, or front-panel display text.

State and persistence: chassis logs and display/LED state may persist in firmware or front-panel hardware until overwritten. Dependencies and integration: used by LED support, platform diagnostics, PDC firmware calls, and proc/status reporting.

Risks and test signals: firmware calls may differ across models; bad lengths or encodings can fail silently. Test with model-specific chassis status output and graceful fallback on systems without chassis display support.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
