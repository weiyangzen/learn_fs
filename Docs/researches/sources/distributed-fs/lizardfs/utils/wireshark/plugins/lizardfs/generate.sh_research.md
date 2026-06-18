# sources/distributed-fs/lizardfs/utils/wireshark/plugins/lizardfs/generate.sh

Purpose: generator wrapper for the LizardFS Wireshark plugin sources.

Important operations: requires a path to `MFSCommunication.h`, canonicalizes it with `readlink -m`, changes to the plugin directory, writes `includes.h` with protocol constants and an include of the input header, then runs `python3 make_dissector.py < "$input_file" > packet-lizardfs.c`.

Control flow: usage validation requires exactly one argument. `set -eu` stops on missing variables and command failures. The generated `includes.h` defines `PROTO_BASE`, `MFSBLOCKSINCHUNK`, `MFSBLOCKSIZE`, and `LIZARDFS_WIRESHARK_PLUGIN` to make protocol macros parse/build outside the main tree.

State and persistence: overwrites `includes.h` and `packet-lizardfs.c` in the plugin directory.

Dependencies/integration: depends on Bash, GNU `readlink -m`, Python 3, the protocol header format, and `make_dissector.py`.

Risks and test signals: generated files are only as accurate as protocol comments/macros in `MFSCommunication.h`. Test signals are regeneration after protocol changes, generated C compilation, and stable diffs when input is unchanged.
