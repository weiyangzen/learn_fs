# sources/distributed-fs/lizardfs/utils/wireshark/plugins/lizardfs/moduleinfo.h

Purpose: Wireshark plugin metadata header for the LizardFS dissector module.

Important content: defines package string as `lizardfs`, major/minor/micro version `1.0.0`, and empty `VERSION_FLAVOR`. It includes the standard Wireshark GPL header comments.

Control flow/state: metadata-only header. It does not declare functions or persistent state.

Dependencies/integration: consumed by Wireshark plugin build/registration conventions alongside `CMakeLists.txt` and generated `plugin.c`/`packet-lizardfs.c`.

Risks and test signals: version drift is the main risk; plugin packaging should match the CMake `set_module_info(lizardfs 1 0 0 0)`. Test signals are successful plugin build and Wireshark module metadata display.
