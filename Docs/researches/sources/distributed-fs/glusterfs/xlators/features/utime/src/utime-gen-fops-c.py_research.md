# sources/distributed-fs/glusterfs/xlators/features/utime/src/utime-gen-fops-c.py

## Purpose
Generates C fop wrappers and callbacks for utime from libglusterfs operation metadata and a template file.

## Important APIs, Types, and Functions
- Imports `ops`, `fop_subs`, `cbk_subs`, and `generate` from `libglusterfs/src/generator.py`.
- Template families generate common fops, read fops, write fops, copy-file-range fops, and special setattr/fsetattr logic.
- `gen_defaults()` emits callback then fop implementation for names selected in `utime_ops`, `utime_read_op`, `utime_write_op`, `utime_setattr_ops`, and `utime_copy_file_range_ops`.
- Main loop copies template lines and replaces `#pragma generate` with generated code markers and generated functions.

## Control Flow
At build time, the script reads the template path from `sys.argv[1]`, scans each line, and prints generated C to stdout. Generated fops set `frame->root->ctime`, call `utime_update_attribute_flags()` or special setattr logic, then wind to the child and unwind in generated callbacks.

## State and Persistence
No persistent state. Output is a generated build artifact.

## Dependencies and Integration Points
Depends on Python 3, relative import of GlusterFS generator metadata, and fop name tables matching current GlusterFS APIs. Integrated by `Makefile.am`.

## Risks
Operation list drift can omit new fops or generate stale signatures. Special setattr logic uses `valid` and `stbuf` names from generator substitutions and is sensitive to signature changes. Generated code uses stdout, so build redirection must remain correct.

## Test Signals
Run generator and compile generated output. Inspect that `readv`, `writev`, `setattr`, `fsetattr`, and `copy_file_range` receive their specialized templates.
