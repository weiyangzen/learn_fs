# sources/distributed-fs/ceph-client/arch/sh/cchips/hd6446x/Makefile



Source read size: 4 lines, 97 bytes.



Purpose: builds HD64461 companion-chip support when selected.

Important APIs/types/functions: `obj-$(CONFIG_HD64461) += hd64461.o` and `ccflags-y := -Werror`.

Control flow: Kbuild includes `hd64461.o` only for HD64461-enabled configurations and treats warnings in this directory as errors.

State and persistence: build-time object selection only.

Dependencies and integration points: tied to the companion-chip Kconfig and generic SH driver build.

Risks and test signals: `-Werror` can turn compiler-version warning drift into build failures. Test HD64461 and non-HD64461 configs.
