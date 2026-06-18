# sources/distributed-fs/openafs/src/tools/dumpscan/afsdump_xsed.c

Purpose: older or alternate dump scanner/rewriter based on the UB/MR-AFS code path. It resembles `afsdump_scan` but adds `-A nnn` to grant all directory ACL rights to a specified ID while generating a repaired dump.

Important APIs/functions: it contains local `parse_printflags`, `parse_repairflags`, `parse_options`, `print_vnode_path`, `munge_admin_acl`, and `setup_repair`. `munge_admin_acl` edits the on-dump ACL buffer in a directory vnode, inserting the ID into positive rights or removing it from negative rights, then delegates to `repair_vnode_cb`.

State/dependencies: in repair mode it writes `repair_output`; with `-A` it mutates directory ACLs in the generated dump. It depends on `dumpscan.h`, repair callbacks, OpenAFS ACL rights constants, and seekable `XFILE` input for path or repair modes.

Risks/test signals: this file appears less maintained than `afsdump_scan.c`: option string omits `q` although the switch handles it, `my_error_cb` lacks an explicit return, `setup_repair` and `xfopen` calls use older argument conventions, and the known-type test uses `||` where `&&` was likely intended. It should be treated cautiously unless its target is still built in a matching legacy environment.
