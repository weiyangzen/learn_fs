# File Research: sources/block-storage/thin-provisioning-tools/src/commands/mod.rs

Command module registry and shared command trait.

Exports production command modules:
- Cache: check, dump, metadata_size, repair, restore, writeback.
- Era: check, dump, invalidate, repair, restore.
- Thin: check, delta, dump, ls, metadata pack/size/unpack, migrate, repair, restore, rmap, shrink, trim.
- Shared `engine` and `utils`.

Feature-gated devtools:
- Cache damage/generation.
- Era metadata generation.
- Thin explore, damage/generation, stat.

Defines `Command<'a>` trait with `name()` and `run(args)` returning an exit code.
