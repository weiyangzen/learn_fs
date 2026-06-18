# File Research: sources/block-storage/lvm2/tools/command-lines.in

Purpose: declaratively defines LVM command syntaxes, common option groups, optional/required arguments, command IDs, descriptions, inferred types, implicit options, and validation rules.

Read coverage: complete file read, 2,158 lines.

Key responsibilities:
- Documents the command-definition grammar used by the LVM command parser and help/man generator.
- Defines common option groups such as `OO_ALL`, `OO_REPORTING`, `OO_REPORT`, `OO_CONFIG`, and command-family groups for lvchange, lvconvert, lvcreate, vgchange, and others.
- Describes how required options, optional options (`OO:`), optional positional arguments (`OP:`), ignored/internal options (`IO:`), command IDs, descriptions, rules, flags, and `AUTOTYPE` annotations work.
- Encodes command families for `lvchange`, `lvconvert`, `lvcreate`, `lvdisplay`, `lvextend`, `lvmconfig`, `lvmdevices`, `lvreduce`, `lvremove`, `lvrename`, `lvresize`, `lvs`, `lvscan`, PV commands, VG commands, reports, built-ins, and deprecated commands.
- Captures many historical/secondary syntaxes through `FLAGS: SECONDARY_SYNTAX` and `FLAGS: PREVIOUS_SYNTAX`.
- Uses `RULE:` lines to reject invalid option combinations, LV types, and LV properties after command matching.
- Uses `AUTOTYPE:` to document or validate inferred segment types without making `--type` part of the matching key.
- Assigns stable `ID:` strings that map syntactic variants to implementation handlers and command counts.

Major command areas:
- LV conversion definitions cover RAID/mirror type conversions, split/merge flows, thin/cache/writecache/VDO pool conversion, cache attach/detach, metadata swap, repair/replace, polling, and RAID integrity.
- LV creation definitions cover linear, striped, mirror, RAID, COW snapshots, thin pools, thin volumes, cache pools, cache/writecache attach flows, and VDO volumes.
- PV/VG command definitions cover creation, resize, metadata repair/check, devices file management, activation, locking, persistent reservations, import/export, split/merge/reduce/remove/rename, reports, and display variants.
- Built-in/deprecated definitions preserve compatibility for aliases such as `config`, `dumpconfig`, `pvdata`, `vgconvert`, `lvmdiskscan`, `lvmsadc`, and `lvmsar`.

Dependencies:
- Option names must correspond to canonical entries in `args.h`, with documented synonym translation.
- Value types must correspond to parser types in `tools/vals.h`.
- `Makefile.in` embeds this file into `command-lines-input.h` and counts `ID:` lines for `command-count.h`.
- Runtime command parsing and generated documentation rely on this declarative data.

Risk and edge cases:
- The file explicitly documents ambiguous syntaxes where command matching cannot distinguish LV types before metadata is read.
- Some validations cannot be expressed in command definitions and are deferred to command implementations.
- Order matters where ambiguous definitions could match the same user input.
- Comments note inconsistent historical behavior for thin/cache/type variants, making regression risk high when editing.
- `--size`/`--extents` alternation and lvcreate VG/name inference are handled automatically outside the literal definitions.
- Generated command input omits comments, separators, and blank lines; only definition lines affect runtime metadata.
