# sources/distributed-fs/lizardfs/src/mount/client/client.cc

## Purpose
`client.cc` implements the C++ object wrapper `lizardfs::Client` around the singleton-style `LizardClient` namespace. It dynamically loads a mount shim, resolves unmangled function exports, converts integer status codes to `std::error_code`, and manages open file/directory handles.

## Important APIs, Types, And Functions
- `Client::linkLibrary()` loads `liblizardfsmount_shared.so`; for multiple instances it copies the shared object to a temporary file so each instance gets isolated singleton state.
- Constructors initialize `FsInitParams` and call `init`.
- Destructor releases tracked fileinfos, terminates the filesystem, closes the dynamic library, and decrements instance count.
- `init` resolves all `lizardfs_*` symbols via `dlsym` and calls `lizardfs_fs_init`.
- Methods wrap metadata, directory, file IO, xattr, ACL, chunk info, chunkserver info, and lock operations in throwing and `std::error_code` forms.
- `toXattrList` parses null-separated xattr names into strings.

## Control Flow
Every public throwing overload creates a local `std::error_code`, calls the corresponding nonthrowing overload, and throws `std::system_error` on failure. Nonthrowing overloads call resolved C-linkage function pointers, assign `ec = make_error_code(ret)`, and return output values. `open`/`opendir` allocate `FileInfo` and push it into an intrusive list under mutex; `release`/`releasedir` remove and delete. `read` dispatches to special-inode or regular read wrappers. `setlk` is split into send, optional interrupt-registration callback, and blocking receive.

## State And Persistence
Per instance state includes a dynamic library handle, resolved function pointers, an intrusive list of live `FileInfo` objects, a mutex, and an atomic opendir session id. Static `instance_count_` controls first-instance direct loading versus temp-copy loading. Persistent filesystem effects are performed by the underlying LizardClient/mount functions.

## Dependencies And Integration Points
It depends on `lizard_client_c_linkage.h`, `client_error_code.h`, `richacl_converter`, POSIX `dlopen/dlsym/dlclose`, and the installed `LIB_PATH`. It is the backend for `lizardfs_c_api.cc` and for C++ consumers of `lizardfs-client-cpp`.

## Risks
- Several throwing overloads appear to recurse into themselves instead of calling the `std::error_code` overload: `readlink(Context&,Inode)`, `fsync(Context&,FileInfo*)`, and `setacl(Context&,Inode,const RichACL&)`. These would cause infinite recursion/stack overflow when used.
- `mkdir(Context&,...)` throwing overload calls the nonthrowing overload but does not check `ec` and throw.
- `linkLibrary` copies the shared object with stream insertion without checking source/destination open/write errors.
- Temporary library copy uses `/tmp` and unlinks after `dlopen`; failures before close/unlink can leak fd/path briefly.
- Destructor releases all fileinfos while invoking methods that also lock/modify the list; correctness depends on list operations and no external concurrent use during destruction.

## Test Signals
Tests should instantiate multiple clients, verify independent dynamic state, assert every `dlsym` is required, exercise throwing vs nonthrowing overloads, detect recursion bugs, and verify fileinfo tracking across open/release/opendir/releasedir/destructor. ABI tests should load the built `lizardfsmount_shared`.
