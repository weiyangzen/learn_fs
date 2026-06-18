# sources/distributed-fs/ceph-client/include/soc/imx/revision.h

Purpose: defines i.MX silicon revision constants and revision query/printing APIs.

Important APIs and types: macros encode revisions 1.0 through 3.3 and unknown as compact hex values. Functions query specific MX25/MX27/MX31/MX35/MX51/MX53 revisions, return generic SoC revision via `imx_get_soc_revision()`, and print silicon revision strings with `imx_print_silicon_rev()`.

Control flow: platform initialization detects SoC revision, stores it in platform state, and drivers call revision helpers to apply errata or report silicon versions.

State and persistence: detected revision is runtime platform state derived from hardware fuses/registers. No persistent state is stored by the header.

Dependencies and integration points: used by i.MX platform/driver errata handling and boot logging.

Risks and test signals: risks include treating `UNKNOWN` as a valid comparable revision, applying errata to wrong families, and missing helper implementations in configs. Test revision reads on supported SoCs, boot log formatting, errata quirk paths, and compile/link coverage for all declared helpers.
