<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/cfg.mk -->
## sources/cloud-native/ostree/cfg.mk

### Purpose
This maintainer-check configuration customizes gnulib/maint.mk source checks and version-control file exclusions for OSTree.

### APIs, Types, and Control Flow
It exports `VC_LIST_EXCEPT_DEFAULT` to exclude Rust bindings, docs, git.mk, support directories, gettext header, changelogs, and buildutil from default checks. It skips many generic maintainer checks that do not fit the project. It defines two custom syntax checks prohibiting trailing colons in `glnx_prefix_error()` and `glnx_throw_errno_prefix()` messages, a `show-vc-list-except` helper, and always-exclude regexes for metadata/compressed/signature files.

### State, Dependencies, and Integration
It is included by `GNUmakefile` and works with maintainer check machinery plus `build-aux/vc-list-files`.

### Risks and Test Signals
Skipping checks reduces noise but can hide portability/style issues. Custom regexes are grep-based and may produce false positives/negatives. Test signal is maintainer `make syntax-check` behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/cfg.mk -->
