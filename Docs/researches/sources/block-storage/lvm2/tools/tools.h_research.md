# File Research: sources/block-storage/lvm2/tools/tools.h

Purpose: central public header for LVM2 command-line tools, tying together tool framework headers, command prototypes, command argument parsing/lookup APIs, and cross-command helper declarations.

Read coverage: complete file read, 254 lines.

Key responsibilities:
- Includes the main tool, toollib, logging, activation, archiver, lvmcache, locking, config, device, display, metadata, exec, signal, string, segtype, toolcontext, notify, and hints interfaces needed by tool implementations.
- Declares command entry points by macro-expanding `commands.h` through `xx(a, b...)`.
- Defines command argument flags such as countable, groupable, noninteractive-only, and long-option.
- Defines `struct arg_values` and grouped argument storage used by parsed command options.
- Declares value parsing/normalization callbacks for booleans, activation, cache settings, sizes, extents, tags, permissions, segment types, lock types, reporting formats, config types, repair/dump/headings values, and more.
- Declares argument accessors for set/count/value/sign/percent/grouped forms.
- Declares shared command helpers for activation, background polling, vgchange subcommands, lvchange/lvconvert/lvcreate/lvresize subcommands, display variants, and PV scan variants.

Dependencies:
- Depends on command metadata generated through `command.h` and `commands.h`.
- Exposes APIs used throughout `tools/*.c` and relies heavily on `cmd_context`, metadata structs, `processing_handle`, `activation_change_t`, and command enum/arg enum definitions.

Risks and edge cases:
- Because this is a broad aggregation header, changes can trigger wide rebuilds and unintended dependency coupling.
- Argument accessor contracts must stay synchronized with generated command definitions and `vals.h`/`args.h`.
- Generated command prototype expansion depends on `xx` macro shape, so include ordering and macro cleanup matter.
