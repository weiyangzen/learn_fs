# File Research: sources/block-storage/lvm2/tools/commands.h

## Purpose
`commands.h` is the top-level LVM command registry. It is a macro table using `xx(command, description, flags)` entries.

## Contents
The file lists user-facing commands such as `dumpconfig`, `formats`, `lvchange`, `lvconvert`, `lvcreate`, `lvdisplay`, `lvs`, PV/VG commands, reporting commands, and compatibility/removed commands.

Each entry provides a stable command name, short description, and command policy flags.

## Integration Notes
The file is included multiple times under different `xx` definitions to generate command-name tables, command enums, and command metadata. Changes affect command availability, help text, locking behavior, all-VG defaults, and metadata-processing policy.
