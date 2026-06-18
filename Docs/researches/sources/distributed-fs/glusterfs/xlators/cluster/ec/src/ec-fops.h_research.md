# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-fops.h

Purpose: declares the EC translator's full fop wrapper surface. These functions are the internal entry points used by Gluster fop tables, EC sub-operations, and common repair/dispatch code.

Important APIs: prototypes cover metadata, namespace, file data, xattr, lock, heal, seek, ipc, and directory operations: access/create/entrylk/fentrylk/flush/fsync/fsyncdir/getxattr/fgetxattr/heal/fheal/inodelk/finodelk/link/lk/lookup/mkdir/mknod/open/opendir/readdir/readdirp/readlink/readv/removexattr/fremovexattr/rename/rmdir/setattr/fsetattr/setxattr/fsetxattr/stat/fstat/statfs/symlink/fallocate/discard/truncate/ftruncate/unlink/writev/xattrop/fxattrop/seek/ipc.

Control flow and integration: every prototype follows the EC pattern: caller frame, translator, target mask, fop flags, typed callback, callback data, fop-specific arguments, and xdata. Implementations allocate `ec_fop_data_t`, populate fields, then call `ec_manager()` with fop-specific manager/wind callbacks. The header includes `ec-types.h` and `ec-common.h`, so it also imports shared fop flag/minimum semantics.

State behavior: this header stores no state but defines the ABI through which stateful managers receive loc/fd/dict/iovec/lock arguments. Risks are signature drift against Gluster fop table typedefs, callback union mismatches, and accidental omission when new fops are added to the translator. Test signals include full translator build with `-Werror` prototypes, fop-table initialization coverage, and smoke tests that exercise every declared wrapper through mounted EC volumes or targeted translator tests.
