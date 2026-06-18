# sources/distributed-fs/openafs/src/config/Makefile.version-CML.in

Purpose: version-generation make fragment for builds using the historical CML state/stamps mechanism.

Important APIs/types/functions: defines `PACKAGE`, `VERSION`, and rules for `AFS_component_version_number.c`, `AFS_component_version_number.h`, `version.txt`, and `version.xml`, all produced by `config/mkvers`.

Control flow: targets invoke `mkvers` with output-format switches: default C source, `-v` for NT version info header, `-t` for text, and `-x` for XML. Comments note mkvers performs timestamp checks.

State and persistence: writes generated version files reflecting CML state and stamps.

Dependencies and integration: selected by `src/config/Makefile.in` when `CML/state` exists. Consumed by object files embedding OpenAFS component version strings and release metadata.

Risks and test signals: risks include absent CML files, stale timestamp comparisons, and format drift. Signals are correct generated C/header/text/XML version outputs for a CML checkout.
