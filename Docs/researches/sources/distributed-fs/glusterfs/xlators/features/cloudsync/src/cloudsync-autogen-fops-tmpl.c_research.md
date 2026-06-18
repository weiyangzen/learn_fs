# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-autogen-fops-tmpl.c

## Purpose
C source template used by `cloudsync-fops-c.py` to generate default cloudsync fop wrappers.

## Important APIs, types, and functions
The template includes GlusterFS xlator/defaults headers plus `cloudsync.h`, `cloudsync-common.h`, and call-stub APIs. The only generator hook is `#pragma generate`.

## Control flow
The Python generator copies ordinary template lines and replaces `#pragma generate` with generated callback, resume, and fop implementations for selected operations.

## State and persistence behavior
The template has no runtime state. Its generated output becomes `cloudsync-autogen-fops.c`, which is compiled into the translator.

## Dependencies and integration points
Depends on the generator scripts and the `generator.py` operation metadata. Integrates with `cloudsync.c` because generated fops call shared helpers such as `cs_local_init`, `locate_and_execute`, `cs_resume_postprocess`, and `CS_STACK_UNWIND`.

## Risks and test signals
Any include cycle or missing prototype can break generated code. Tests should compare generated output after operation table updates and compile cloudsync with warnings enabled.
