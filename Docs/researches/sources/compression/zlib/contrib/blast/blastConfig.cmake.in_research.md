# sources/compression/zlib/contrib/blast/blastConfig.cmake.in

Purpose: installed CMake package configuration template for `find_package(blast CONFIG)`.

Important variables/control: `_blast_supported_components` contains `shared` and `static`. Requested `blast_FIND_COMPONENTS` drive optional inclusion of `blast-<component>.cmake`; no-components mode includes both component exports and requires both targets to exist.

Control flow: for each requested component, rejects unsupported names, includes the component export file, and sets `blast_<component>_FOUND`. Without components, attempts to include both exports and marks package not found if either `BLAST::BLAST` or `BLAST::BLASTSTATIC` is missing.

State and persistence: executed during downstream CMake configure; sets `blast_FOUND`, `blast_NOT_FOUND_MESSAGE`, and component variables.

Dependencies and integration: generated and installed by blast CMakeLists. Tested by package consumer templates under `contrib/blast/test`.

Risks: no-components mode requires both shared and static targets, which can surprise consumers of shared-only or static-only installs. Error messages mention `ZLIB::ZLIB` target names, likely copy/paste from zlib and misleading for blast.

Test signals: `find_package_no_components` and `find_package_wrong_components` tests intentionally cover success/failure behavior.
