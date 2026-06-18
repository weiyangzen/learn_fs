# Research: sources/distributed-fs/ceph-client/arch/alpha/boot/stdio.c

`stdio.c` supplies a tiny formatting library for bootloader code that cannot rely on the full kernel printf implementation. It implements `strnlen`, `vsprintf`, `sprintf`, numeric formatting, field width, precision, flags, and common integer/string/pointer conversions.

Important helpers are `skip_atoi`, the `do_div` macro, `number`, `vsprintf`, and `sprintf`. Control flow follows classic Linux early-boot formatting: parse flags, width, precision, qualifier, switch on conversion, and write into a caller-supplied buffer without bounds checking.

State is purely stack/local except the caller-provided output buffer. Integration is with `srm_printk` and boot code that needs formatted firmware output. Risks are expected for this era of code: no `snprintf` bounds, limited qualifier support, no modern format extensions, and dependence on boot code not formatting untrusted or oversized strings. Useful test signals are Alpha defconfig or cross-build coverage, sparse/header dependency checks, and targeted boot-image build checks. Runtime validation normally requires Alpha SRM/QEMU or real hardware because many paths depend on PALcode, HWRPB data, chipset registers, or old ISA/PCI behavior.
