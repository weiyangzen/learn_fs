# sources/distributed-fs/openafs/src/config/Makefile.version-NOCML.in

Purpose: version-generation make fragment for normal non-CML builds.

Important APIs/types/functions: defines `PACKAGE`, generates `AFS_component_version_number.c` using `build-tools/git-version`, honors `SOURCE_DATE_EPOCH` for reproducible dates, writes `AFSVersion`, and creates simple `version.xml` and fallback `version.txt`.

Control flow: the C target writes a `.NEW` file, compares it with the current generated source, and moves it only when content changes. Without `SOURCE_DATE_EPOCH`, the string includes current date, user, and hostname; with it, the date comes from the epoch using GNU or BSD `date` syntax.

State and persistence: writes generated version C/XML/text files in the object directory.

Dependencies and integration: selected by `Makefile.in` when no `CML/state` exists; depends on `build-tools/git-version`, shell, date, cmp, and mv. The generated C is compiled into components that expose version strings.

Risks and test signals: risks include reproducibility breaks, date portability, missing git metadata, and non-atomic failure around `.NEW`. Signals are deterministic output with `SOURCE_DATE_EPOCH`, correct package/version strings, and no rebuild when content is unchanged.
