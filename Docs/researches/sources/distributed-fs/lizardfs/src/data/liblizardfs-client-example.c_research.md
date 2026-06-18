# sources/distributed-fs/lizardfs/src/data/liblizardfs-client-example.c

Purpose: executable example for the public LizardFS C client API, demonstrating connection setup, file operations, chunkserver listing, ACLs, and POSIX-style locks.

Important APIs/functions: uses `liz_create_context`, `liz_set_default_init_params`, `liz_init_with_params`, `liz_mknod`, `liz_lookup`, `liz_open`, `liz_write`, `liz_read`, `liz_get_chunkservers_info`, ACL helpers (`liz_create_acl`, `liz_add_acl_entry`, `liz_setacl`, `liz_getacl`, `liz_print_acl`), lock helpers (`liz_setlk`, `liz_getlk`), and cleanup APIs. `register_interrupt` copies lock interrupt data into caller storage.

Control flow: connects to `localhost` using a port from argv or `9421`, recreates `testfile`, opens it, writes and reads sample bytes, prints chunkserver information, creates and round-trips an ACL, exercises lock set/query/unlock cases, then registers an interrupt callback for a conflicting lock scenario. Error paths jump to cleanup labels and return `liz_error_conv(liz_err)`.

State and persistence: creates and modifies `/testfile` under the LizardFS root, sets ACLs and locks on it, and prints status; context, connection, fileinfo, ACLs, and chunkserver info are explicitly destroyed/released.

Dependencies and integration: includes installed public headers `lizardfs/lizardfs_c_api.h` and `lizardfs/lizardfs_error_codes.h`; built by `src/data/CMakeLists.txt` under `BUILD_TESTS`.

Risks: hard-coded password `test123`, root inode, filename, and localhost master make it an example rather than a generic test. Some cleanup paths skip destroying an ACL allocated immediately before errors, so it is not a leak-free template for production code.

Test signals: compilation/linking under `BUILD_TESTS` checks API availability; runtime requires a live LizardFS master.
