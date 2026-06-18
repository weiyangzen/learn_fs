# subset-b-007091 GlusterFS changelog, cloudsync, compress, and gfid-access research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog.c -->
# sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog.c

## Purpose
Implements the GlusterFS `changelog` feature translator. It intercepts selected filesystem operations, records data/metadata/entry changes into changelog journals, dispatches live notification events, and coordinates snapshot barriers so geo-replication and glusterfind consumers see a consistent operation stream.

## Important APIs, types, and functions
The exported translator entry points are `init`, `fini`, `reconfigure`, `notify`, `mem_acct_init`, the `fops` table, and `cbks.release`. Entry fops include `changelog_mknod`, `mkdir`, `create`, `symlink`, `link`, `rename`, `unlink`, and `rmdir`; metadata fops include `{f,}setattr`, `{f,}setxattr`, `{f,}removexattr`, `{f,}xattrop`; data fops include `{f,}truncate` and `writev`. Callback pairs call `changelog_update()` on successful child completion. Helper routines configure operation mode, encoding, barrier timeout, helper threads, RPC notification, and option cleanup.

## Control flow
Each logged fop first checks whether changelog is active and whether the request is internal/rebalance/shard-excluded where applicable. It initializes a `changelog_local_t`, fills encoded changelog records with fop number, gfid, mode/uid/gid, or entry names, and either winds immediately or queues a call stub behind the changelog barrier. On callback success, it updates the log as `CHANGELOG_TYPE_DATA`, `METADATA`, `METADATA_XATTR`, or `ENTRY`, decrements barrier fop counters, and unwinds. Barrier `notify()` requests start or stop snapshot logging, flip `barrier_ext`, enable/disable queuing, wake rollover through a pipe, and drain queued operations.

## State and persistence behavior
Persistent output is the changelog directory tree, htime data, csnap logging, and per-slice changelog files written by the runtime backend selected from `cb_bootstrap`. Durable options are `changelog-dir`, `encoding`, `rollover-time`, `fsync-interval`, and delete-path capture. Runtime state lives in `changelog_priv_t`: active/rpc flags, current color, fop counters, queue, pthread condition variables, RPC service/listeners, rolling buffers, helper thread ids, htime fd, changelog fd, and event selection. Per-operation state is in `frame->local` and is cleaned through changelog unwind macros.

## Dependencies and integration points
Depends on Gluster xlator stack APIs, changelog runtime/encoder/RPC headers, call stubs, dictionaries, mem pools, pthreads, htime/csnap helpers, and RPC service cleanup. Integrates with geo-replication/glusterfind through journal files and with live consumers through `changelog_dispatch_event()`, open/create/release events, IPC event dispatch, and Unix-domain changelog RPC sockets. DHT special rename metadata and shard/tier internal markers influence what is recorded.

## Risks and test signals
High-risk areas are barrier races, counter/color ordering, queued stub allocation failure, helper thread cleanup, RPC listener teardown during parent-down, htime/csnap rollover, and option reconfigure while active. The source contains apparent duplicate tokens near `changelog_unlink` and `changelog_link` in this snapshot, which is a build-risk signal. Tests should exercise all logged fops with active/inactive changelog, internal fop suppression, DHT rename-as-unlink, delete-path capture, virtual `GF_XATTR_TRIGGER_SYNC`, barrier on/off/timeout, RPC notification enablement, reconfigure from inactive to active, and cleanup during parent down.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/cloudsync/Makefile.am

## Purpose
Top-level Automake file for the `cloudsync` feature translator directory. It delegates all real build work to `src`.

## Important APIs, types, and functions
No code APIs are declared. The build API is `SUBDIRS = src`, with an empty `CLEANFILES`.

## Control flow
During recursive Automake builds, this directory enters `src`, where the translator, generated fops, shared common code, and plugin subdirectories are built.

## State and persistence behavior
No runtime state or generated artifacts are produced here directly.

## Dependencies and integration points
Integrates the cloudsync subtree into the larger GlusterFS recursive build. Its only dependency is the existence of `src/Makefile.am`.

## Risks and test signals
Risk is low. Build validation should confirm recursive make enters `xlators/features/cloudsync/src` and that clean/install targets are handled by deeper Makefiles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/Makefile.am

## Purpose
Builds the `cloudsync.la` xlator module, shared cloudsync common source, generated fop code, and plugin subtree.

## Important APIs, types, and functions
Defines `cloudsync_la_SOURCES = cloudsync.c cloudsync-common.c`, `nodist_cloudsync_la_SOURCES = cloudsync-autogen-fops.c cloudsync-autogen-fops.h`, and generation rules invoking `cloudsync-fops-c.py` and `cloudsync-fops-h.py` over template files. It defines `CS_PLUGINDIR` as an install-time plugin path used by `dlopen()` in `cloudsync.c`.

## Control flow
Automake first descends into `cloudsync-plugins`, generates the autogen C and H from Python scripts and templates, compiles the module with `LIB_DL`, and installs it under GlusterFS feature xlator directory. `uninstall-local` removes `cloudsync.so`.

## State and persistence behavior
Persists generated build outputs `cloudsync-autogen-fops.c` and `.h` during the build and cleans them through `CLEANFILES`.

## Dependencies and integration points
Depends on `libglusterfs`, dynamic loader support, GlusterFS RPC/XDR include paths, and Python generator infrastructure under `libglusterfs/src`. The plugin install path must match the plugin Makefiles that install `cloudsyncs3.so` and `cloudsynccvlt.so`.

## Risks and test signals
Risks include stale generated fops, missing Python generator modules, and mismatch between `CS_PLUGINDIR` and installed plugin names. Build tests should run from a clean tree, verify generated files are rebuilt, and confirm `cloudsync.la` links with `LIB_DL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-autogen-fops-tmpl.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-autogen-fops-tmpl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-autogen-fops-tmpl.h -->
# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-autogen-fops-tmpl.h

## Purpose
Header template used by `cloudsync-fops-h.py` to generate prototypes for cloudsync fops.

## Important APIs, types, and functions
It defines include guard `_CLOUDSYNC_AUTOGEN_FOPS_H`, includes GlusterFS xlator plus cloudsync headers, and exposes `#pragma generate` as the insertion point for generated `cs_<fop>()` declarations.

## Control flow
The generator emits “BEGIN GENERATED CODE” and one prototype for every supported operation except `getspec`.

## State and persistence behavior
No runtime state. Generated output is `cloudsync-autogen-fops.h`, included by `cloudsync.h` and compiled users.

## Dependencies and integration points
Coupled to the operation metadata in `libglusterfs/src/generator.py` and to generated C function names.

## Risks and test signals
Prototype drift between generated C and H breaks builds. Test by regenerating both files and compiling all cloudsync fop table references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-autogen-fops-tmpl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-common.c -->
# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-common.c

## Purpose
Owns cleanup helpers for per-frame cloudsync state and remote-read xattr metadata.

## Important APIs, types, and functions
`cs_xattrinfo_wipe()` frees `cs_loc_xattr_t` fields attached under `local->xattrinfo.lxattr`. `cs_local_wipe()` releases copied `loc_t`, referenced `fd_t`, pending call stub, request/response dictionaries, anonymous download fd, remote path string, xattr info, and finally returns `cs_local_t` to the local mem pool.

## Control flow
Cloudsync unwind macros detach `frame->local`, unwind/destroy the stack, and call these cleanup routines. Error paths in stat checking and postprocess also depend on them to dispose partially initialized state.

## State and persistence behavior
No durable state. It manages transient ownership of refs and heap allocations stored in `cs_local_t`.

## Dependencies and integration points
Depends on GlusterFS loc/fd/dict/call-stub APIs and the cloudsync mem pool created by `cs_init`. Used by both the translator and plugin builds because plugin Makefiles compile `cloudsync-common.c` into plugin modules.

## Risks and test signals
Risks are double unrefs when callbacks reuse `dlfd`, stale `frame->local`, and leaks on partially initialized `xattrinfo`. Tests should cover unwind after failed stub creation, failed xattr extraction, remote read callback, and download failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-common.h -->
# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-common.h

## Purpose
Defines common cloudsync state structures, plugin function-pointer contracts, private translator state, and stack cleanup macros shared by translator and plugins.

## Important APIs, types, and functions
Key types are `cs_loc_xattr_t`, `cs_size_xattr_t`, `cs_local_t`, `cs_private_t`, `cs_remote_stores`, and `store_methods_t`. Function pointer contracts include plugin download, remote read, init, reconfigure, and fini hooks. `CS_STACK_UNWIND` and `CS_STACK_DESTROY` centralize frame-local cleanup.

## Control flow
Cloudsync fops allocate `cs_local_t`, set `local->fop`, request object status xattrs, and either wind to child or call plugin hooks. Plugins export a `store_ops` symbol matching `store_methods_t`; `cs_init()` loads it with `dlsym()`.

## State and persistence behavior
State is transient except that plugin hooks interpret persisted xattrs such as remote object path, archive UUID, and object status. `cs_private_t` holds the loaded plugin, plugin config, abort flag, spinlock, and remote-read mode.

## Dependencies and integration points
Depends on GlusterFS call-stub, syncop, compat errno, memory types, and message headers. It is the ABI boundary between cloudsync core and `cloudsyncs3`/`cvlt` plugin modules.

## Risks and test signals
The ABI is C-struct/function-pointer based, so field order and symbol visibility matter. Tests should load every plugin, verify missing hooks fail cleanly, and run fop error paths to confirm stack cleanup happens once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-fops-c.py -->
# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-fops-c.py

## Purpose
Generates C implementations for cloudsync fops that follow repeated patterns: data-modifying fd operations that may recall a remote file, and loc-based status operations that refresh inode state.

## Important APIs, types, and functions
Imports `ops`, substitutions, and `generate()` from GlusterFS `generator.py`. Templates emit `cs_<name>_cbk`, `cs_resume_<name>`, and `cs_<name>` for fd data-modifying operations, and `cs_<name>_cbk`/`cs_<name>` for loc stat-like operations.

## Control flow
For fd data-modifying ops, generated fops validate inputs, allocate `cs_local_t`, read inode context, request `GF_CS_OBJECT_STATUS`, create a resume stub, wind to the child if local, or take the cloudsync inodelk and stat/repair path if remote/downloading. Callbacks update inode state and retry through `locate_and_execute()` once. Loc stat fops request object status and update/reset inode context in callbacks.

## State and persistence behavior
Generated code updates in-memory inode context and passes xdata requests to lower translators that know cloudsync object status. No durable storage is written directly.

## Dependencies and integration points
Depends on generator metadata, cloudsync helper prototypes, `GF_CS_OBJECT_STATUS`, `CS_STACK_UNWIND`, call stubs, and lower child fops. Generated functions are referenced in `cs_fops` for operations not manually implemented in `cloudsync.c`.

## Risks and test signals
Risks include operation-list drift, generated code using wrong callback error arguments, dictionary ownership mistakes, and untested multi-op combinations. Regeneration and compile tests are essential after changes to GlusterFS fop signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-fops-c.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-fops-h.py -->
# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-fops-h.py

## Purpose
Generates declarations for all cloudsync fop wrappers.

## Important APIs, types, and functions
Imports operation metadata from `generator.py`, skips `getspec`, and emits one `int32_t cs_<name>(call_frame_t *, xlator_t *, ...)` prototype per operation.

## Control flow
Reads the template path given on argv, replaces `#pragma generate` with generated declarations, and preserves all other template lines.

## State and persistence behavior
No runtime state. Its output persists as build-generated `cloudsync-autogen-fops.h`.

## Dependencies and integration points
Coupled to C generation and to the `cs_fops` table. It relies on `fop_subs` to match current GlusterFS fop signatures.

## Risks and test signals
Signature mismatch with generated C or xlator fops causes compile failures. Test by regenerating from a clean build and validating no stale prototypes remain.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-fops-h.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-mem-types.h

## Purpose
Defines memory accounting tags for the cloudsync translator.

## Important APIs, types, and functions
Enum values cover `cs_private_t`, `cs_remote_stores`, `cs_inode_ctx_t`, and `cs_loc_xattr_t`, ending at `gf_cs_mt_end`.

## Control flow
`cs_mem_acct_init()` registers the range with `xlator_mem_acct_init()`. Allocations in cloudsync use these tags for accounting and diagnostics.

## State and persistence behavior
No runtime persistence. It affects memory accounting categorization.

## Dependencies and integration points
Includes GlusterFS common memory type definitions. Used by `cloudsync.c` and `cloudsync-common.c`.

## Risks and test signals
Memory tag overlap can corrupt accounting. Test by enabling memory accounting and checking cloudsync allocation classes during init, fop, and teardown paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-messages.h -->
# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-messages.h

## Purpose
Placeholder for structured cloudsync message IDs.

## Important APIs, types, and functions
Only defines include guard `__CLOUDSYNC_MESSAGES_H__`; a TODO notes that message IDs should be added.

## Control flow
No executable control flow.

## State and persistence behavior
No state or persistence.

## Dependencies and integration points
Included by `cloudsync-common.h`, so future message IDs here would be available across core cloudsync code.

## Risks and test signals
Because most cloudsync logging currently uses numeric zero IDs, diagnostics are less structured. Tests are not applicable beyond ensuring the header remains include-safe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/Makefile.am

## Purpose
Top-level plugin subtree Makefile for cloudsync plugins.

## Important APIs, types, and functions
Build directive is `SUBDIRS = src`; no code APIs.

## Control flow
Recursive make descends into `src`, where conditional plugin directories are selected.

## State and persistence behavior
No direct state or artifacts beyond recursive build traversal.

## Dependencies and integration points
Integrates plugin builds under the cloudsync source build.

## Risks and test signals
Low risk. Build tests should confirm plugin conditionals are evaluated in the child Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/Makefile.am

## Purpose
Selects optional cloudsync plugin subdirectories based on configure-time feature flags.

## Important APIs, types, and functions
If `BUILD_AMAZONS3_PLUGIN` is set, `AMAZONS3_DIR = cloudsyncs3`; if `BUILD_CVLT_PLUGIN` is set, `CVLT_DIR = cvlt`; `SUBDIRS` expands to those enabled directories.

## Control flow
Automake builds only configured plugin directories, allowing cloudsync core to compile without plugin dependencies.

## State and persistence behavior
No runtime state. Build output is controlled indirectly by selected subdirectories.

## Dependencies and integration points
Couples configure flags to plugin modules that cloudsync later loads by name from `CS_PLUGINDIR`.

## Risks and test signals
Risk is deployment mismatch: a volume can request a plugin not built or installed. Tests should cover builds with neither, each, and both plugin flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cloudsyncs3/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cloudsyncs3/Makefile.am

## Purpose
Delegates the Amazon S3 cloudsync plugin build to its `src` directory.

## Important APIs, types, and functions
Only `SUBDIRS = src` and empty `CLEANFILES`.

## Control flow
Recursive make enters the plugin implementation directory.

## State and persistence behavior
No direct state.

## Dependencies and integration points
Part of the conditional S3 plugin build chain.

## Risks and test signals
Low risk; verify recursion reaches `cloudsyncs3/src` when `BUILD_AMAZONS3_PLUGIN` is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cloudsyncs3/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cloudsyncs3/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cloudsyncs3/src/Makefile.am

## Purpose
Builds the `cloudsyncs3.la` plugin module installed under the cloudsync plugin directory.

## Important APIs, types, and functions
Defines `csp_LTLIBRARIES = cloudsyncs3.la`, sources `libcloudsyncs3.c` plus shared `cloudsync-common.c`, exports symbols from `libcloudsyncs3.sym`, and installs to `$(libdir)/glusterfs/$(PACKAGE_VERSION)/cloudsync-plugins`.

## Control flow
Compiles the plugin with GlusterFS include paths, curl/curlpp and crypto flags, links against `libglusterfs`, and leaves the final module available for `dlopen("cloudsyncs3.so")`.

## State and persistence behavior
Build artifact is the installed S3 plugin shared object. No runtime state here.

## Dependencies and integration points
Depends on libcurl, OpenSSL/libcrypto, curlpp flags in the Makefile, and the cloudsync plugin ABI in `cloudsync-common.h`.

## Risks and test signals
Link flags are split between `AM_CPPFLAGS` and `AM_CFLAGS`, which can hide portability problems. Tests should build with S3 enabled, inspect exported `store_ops`, and verify installed file name matches `cloudsync.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cloudsyncs3/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cloudsyncs3/src/libcloudsyncs3-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cloudsyncs3/src/libcloudsyncs3-mem-types.h

## Purpose
Defines memory accounting tags for the S3 cloudsync plugin.

## Important APIs, types, and functions
The enum `libaws_mem_types_` reserves `gf_libaws_mt_aws_private_t` and `gf_libaws_mt_end`.

## Control flow
`mem_acct_init()` in `libcloudsyncs3.c` registers this range for plugin allocations.

## State and persistence behavior
No durable state. It classifies `aws_private_t` allocation.

## Dependencies and integration points
Includes GlusterFS memory type definitions and is included by `libcloudsyncs3.h`.

## Risks and test signals
Header guard end comment references cloudsync rather than AWS, but functionally harmless. Test memory accounting with S3 plugin init/fini.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cloudsyncs3/src/libcloudsyncs3-mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cloudsyncs3/src/libcloudsyncs3.c -->
# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cloudsyncs3/src/libcloudsyncs3.c

## Purpose
Implements the S3 cloudsync plugin that downloads remote object contents via signed HTTP GET and writes them back into the GlusterFS file through the cloudsync recall path.

## Important APIs, types, and functions
Exports `store_ops` with download/init/reconfigure/fini hooks. `aws_private_t` stores hostname, bucket id, access key id, secret key, abort flag, and spinlock. `aws_init()` and `aws_reconfigure()` load S3 options. `aws_form_request()`, `aws_sign_request()`, and `aws_b64_encode()` build AWS Signature V2-style authorization. `aws_download_s3()` drives libcurl. `aws_write_callback()` copies downloaded chunks into iobufs and winds child `writev`; `aws_dlwritev_cbk()` sets abort on write failure.

## Control flow
Cloudsync calls `aws_download_s3(frame, config)` after stat repair finds a remote path. The plugin forms a resource string from bucket and `local->remotepath`, signs it, sets curl Date/Authorization headers and URL, streams response data into `aws_write_callback()`, and verifies HTTP 200. Each chunk is copied into an iobuf, written to `local->dlfd` at `local->dloffset`, and advances the offset.

## State and persistence behavior
Plugin config is in memory. The persistent effect is writing recalled bytes into the GlusterFS object through lower `writev`; cloudsync then removes remote/downloading xattrs. S3 credentials are kept in process memory and logged at debug in this snapshot.

## Dependencies and integration points
Depends on OpenSSL HMAC/BIO APIs, libcurl, GlusterFS iobuf/call-frame APIs, and the cloudsync plugin ABI. It does not implement `fop_remote_read`, so it supports recall/download, not direct remote reads.

## Risks and test signals
Risk signals include apparent bugs in this source snapshot: `aws_fini()` assigns `priv = (aws_private_t *)priv` instead of `config`, `aws_write_callback()` declares `dlfd` twice, and `aws_dlwritev_cbk()` treats `this->private` as `aws_private_t` although it is the translator private. Reconfigure overwrites strings without freeing old values. Tests should cover plugin load, missing credentials, signature generation vectors, curl non-200 responses, child write failure abort, large streaming recall, and fini/reconfigure leak detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cloudsyncs3/src/libcloudsyncs3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cloudsyncs3/src/libcloudsyncs3.h -->
# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cloudsyncs3/src/libcloudsyncs3.h

## Purpose
Declares the S3 plugin API and helper functions used inside `libcloudsyncs3.c`.

## Important APIs, types, and functions
Declares S3 request signing helpers, curl write callback, download entry point, child write callback, plugin lifecycle hooks, and memory/accounting dependencies. Includes `cloudsync-common.h` to expose `store_methods_t` compatibility.

## Control flow
Cloudsync core loads exported `store_ops`; the functions declared here are assigned to that struct inside the plugin C file.

## State and persistence behavior
No state itself. Declared functions operate on plugin config and cloudsync frame state.

## Dependencies and integration points
Includes libcurl and cloudsync common headers, forming the compile-time contract for the S3 plugin.

## Risks and test signals
Header does not declare remote-read support. Tests should ensure symbol export maps match declared lifecycle/download functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cloudsyncs3/src/libcloudsyncs3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cvlt/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cvlt/Makefile.am

## Purpose
Delegates Commvault cloudsync plugin build to its `src` directory.

## Important APIs, types, and functions
Only `SUBDIRS = src`.

## Control flow
Recursive make enters the CVLT implementation directory when enabled.

## State and persistence behavior
No direct runtime state.

## Dependencies and integration points
Part of the conditional CVLT plugin build chain.

## Risks and test signals
Low risk. Verify it is included only under `BUILD_CVLT_PLUGIN`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cvlt/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cvlt/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cvlt/src/Makefile.am

## Purpose
Builds the `cloudsynccvlt.la` Commvault cloudsync plugin module.

## Important APIs, types, and functions
Defines plugin sources as `libcvlt.c` plus shared `cloudsync-common.c`, noinst headers for archive store and CVLT types/messages, and exports symbols from `libcloudsynccvlt.sym`.

## Control flow
Compiles and installs the module under the shared cloudsync plugin directory, where `cloudsync.c` can load `cloudsynccvlt.so` for plugin name `cvlt` on Linux.

## State and persistence behavior
Build artifact is the CVLT plugin shared object.

## Dependencies and integration points
Depends on `libglusterfs`, GlusterFS include trees, and an external runtime `libopenarchive.so` loaded by the plugin implementation.

## Risks and test signals
Risks include symbol export mismatch and runtime dependency not present despite successful build. Tests should build with `BUILD_CVLT_PLUGIN`, inspect exported `store_ops`, and run plugin init with and without `libopenarchive.so`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cvlt/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cvlt/src/archivestore.h -->
# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cvlt/src/archivestore.h

## Purpose
Defines the external archive-store ABI consumed by the CVLT plugin to integrate with `libopenarchive.so`.

## Important APIs, types, and functions
Defines `archstore_desc_t`, `archstore_info_t`, `archstore_fileinfo_t`, callback info, `app_callback_t`, scan type enum, and function pointer typedefs for init, fini, read, recall, restore, archive, backup, and scan. `archstore_methods_t` aggregates the function table. `get_archstore_methods()` is the exported discovery function loaded by `dlsym()`.

## Control flow
`libcvlt.c` loads the archive library, asks for this method table, initializes a descriptor, and then calls `restore()` for recall or `read()` for remote read. Completion is delivered through callbacks or semaphores.

## State and persistence behavior
The header models archive-store identity, product/store id, file UUID/path, and descriptor-private state. Actual durable storage is managed by the external archive library.

## Dependencies and integration points
Depends on `uuid_t`, dynamic loader includes, and C scalar types. It is the hard ABI between GlusterFS CVLT plugin and Commvault/openarchive code.

## Risks and test signals
ABI breakage is the central risk. Tests should validate struct sizes and function table population against the deployed archive library, plus callback error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cvlt/src/archivestore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cvlt/src/cvlt-messages.h -->
# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cvlt/src/cvlt-messages.h

## Purpose
Declares structured message IDs for the CVLT plugin.

## Important APIs, types, and functions
Uses `GLFS_MSGID(CVLT, ...)` to define IDs such as extraction failure, free, resource allocation failure, restore/read failures, no memory, and dlopen failure.

## Control flow
No executable control flow; IDs are consumed by `gf_msg()` calls in `libcvlt.c`.

## State and persistence behavior
No state or persistence.

## Dependencies and integration points
Depends on `glfs-message-id.h` and the CVLT component namespace.

## Risks and test signals
Message IDs should never be deleted or reused. Tests are compile-time plus log inspection for meaningful IDs on failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cvlt/src/cvlt-messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cvlt/src/libcvlt-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cvlt/src/libcvlt-mem-types.h

## Purpose
Defines memory accounting tags for the CVLT plugin.

## Important APIs, types, and functions
Enum `libcvlt_mem_types_` reserves `gf_libcvlt_mt_cvlt_private_t` and `gf_libcvlt_mt_end`.

## Control flow
`mem_acct_init()` in `libcvlt.c` registers this range.

## State and persistence behavior
No runtime persistence; affects memory accounting for `archive_t`.

## Dependencies and integration points
Includes GlusterFS common memory types and is included by `libcvlt.h`.

## Risks and test signals
Low risk. Test memory accounting during CVLT init/fini and request allocation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cvlt/src/libcvlt-mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cvlt/src/libcvlt.c -->
# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cvlt/src/libcvlt.c

## Purpose
Implements the Commvault/openarchive cloudsync plugin, supporting both full recall/download and direct remote reads from an archive store.

## Important APIs, types, and functions
Exports `store_ops` with `cvlt_download`, `cvlt_read`, `cvlt_init`, `cvlt_reconfigure`, and `cvlt_fini`. `archive_t` stores dynamic library handle, request pool, iobuf pool, archive descriptor/method table, product/store IDs, and a trailer guard. `cvlt_extract_store_fops()` loads `libopenarchive.so` and obtains `get_archstore_methods()`. Request helpers allocate/destroy `cvlt_request_t`. `cvlt_download_complete()` posts a semaphore; `cvlt_readv_complete()` unwinds Gluster readv with an iobuf.

## Control flow
Initialization validates graph shape, allocates archive state, creates pools, loads archive methods, initializes the external store, and reads `cloudsync-store-id`/`cloudsync-product-id`. `cvlt_download()` builds source archive and destination Gluster store/file info from `cs_loc_xattr_t`, submits external `restore()`, waits on a semaphore, and returns success/failure to cloudsync recall. `cvlt_read()` validates offset/size, allocates an aligned iobuf, prepares request metadata and size xattrs, submits external `read()`, and returns asynchronously; completion constructs iovec/iobref, adjusts stat size, signals EOF via `ENOENT`, unwinds, and frees the request.

## State and persistence behavior
Runtime state is in `archive_t` and per-request pool objects. Persistent data resides in the external archive store and Gluster file/xattr state that cloudsync supplies. The plugin uses product/store IDs and archive UUID/path xattrs to locate remote objects.

## Dependencies and integration points
Depends on `libopenarchive.so`, `archivestore.h`, GlusterFS iobuf/mempool/locking/logging APIs, semaphores, and cloudsync common state. It is the only plugin here implementing `fop_remote_read`, enabling `cloudsync-remote-read`.

## Risks and test signals
Risks include blocking `sem_wait()` during restore, ABI mismatch with external archive methods, request-pool exhaustion, trailer guard misuse after memory corruption, EOF signaled through `ENOENT`, and async callback lifetime of `frame`/`local`. Source snapshot has duplicate `iov.iov_len = op_ret`. Tests should cover init without `libopenarchive.so`, restore success/failure, remote read at EOF and zero size, callback after failure, concurrent reads up to pool size, and reconfigure of product/store IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cvlt/src/libcvlt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cvlt/src/libcvlt.h -->
# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cvlt/src/libcvlt.h

## Purpose
Declares CVLT plugin structures, operation enum, request state, archive private state, and plugin lifecycle/fop entry points.

## Important APIs, types, and functions
Defines `cvlt_op_t`, `cvlt_request_t`, and `archive_t`. `cvlt_request_t` carries read offsets, byte counts, iobuf/iobref, frame, operation result, semaphore, archive store/file info, and size xattrs. `archive_t` owns locks, xlator pointer, dynamic library handle, pools, archive descriptor, method table, product/store id, and trailer. Declares `cvlt_init`, `cvlt_reconfigure`, `cvlt_fini`, `cvlt_download`, and `cvlt_read`.

## Control flow
`libcvlt.c` allocates `archive_t` during plugin init and allocates `cvlt_request_t` per restore/read. Cloudsync invokes the declared fops through `store_ops`.

## State and persistence behavior
Models in-memory plugin and request state. Persistent remote identity is carried by archive store/file info references populated from xattrs.

## Dependencies and integration points
Depends on semaphores, Gluster compat errno, cloudsync common types, memory tags, and `archivestore.h`.

## Risks and test signals
The structs are internal but tied to async callback lifetime. Tests should validate request cleanup, iobref/iobuf refcounting, and store info validity after reconfigure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cvlt/src/libcvlt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync.c -->
# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync.c

## Purpose
Implements the cloudsync feature translator, which presents archived/remote files through GlusterFS by tracking object state xattrs, recalling data before local modification, and optionally serving reads directly from a remote plugin.

## Important APIs, types, and functions
Lifecycle APIs are `cs_init`, `cs_fini`, `cs_reconfigure`, `cs_notify`, and `cs_mem_acct_init`. Fops include manual implementations for `readdirp`, `truncate`, `setxattr`, `unlink`, `open`, `fstat`, `readv`, and generated fops for many others. Core helpers include `cs_local_init`, `locate_and_execute`, inodelk helpers, `cs_do_stat_check`, `cs_stat_check_cbk`, `cs_resume_postprocess`, `cs_download`, `cs_serve_readv`, inode context helpers, and `cs_common_cbk`.

## Control flow
Init allocates translator private state, local mem pool, loads an optional plugin by `cloudsync-storetype`, resolves `store_ops`, and initializes plugin config. Normal lookup/stat/open/fstat/read/write requests ask the child for `GF_CS_OBJECT_STATUS` so inode context can cache local/remote/downloading/error state. Data-modifying operations on remote/downloading files create a call stub, take an inodelk under `CS_LOCK_DOMAIN`, do a repair stat with object-status and archive-UUID requests, update remote path/xattr info, recall the file through plugin `dlfop`, unlock, and resume the original fop. If `cloudsync-remote-read` is enabled and a file remains `GF_CS_REMOTE`, readv uses plugin `rdfop` instead of recalling.

## State and persistence behavior
In-memory state includes `cs_private_t`, plugin config, per-inode `cs_inode_ctx_t`, and per-frame `cs_local_t`. Persistent behavior is mediated by lower translators and plugins through xattrs such as `GF_CS_OBJECT_STATUS`, `GF_CS_OBJECT_REMOTE`, `GF_CS_OBJECT_DOWNLOADING`, `GF_CS_OBJECT_REPAIR`, `GF_CS_XATTR_ARCHIVE_UUID`, and upload-complete markers. Downloads mark objects as downloading, write data, and remove remote/downloading xattrs.

## Dependencies and integration points
Depends on GlusterFS stack, call stubs, syncop fsetxattr/fremovexattr/ftruncate, dynamic loader, mem pools, inode context APIs, and cloudsync plugin shared objects. Integrates with generated fops, cloudsync-common cleanup, S3/CVLT plugins, and lower storage xattrs.

## Risks and test signals
Risks include plugin load failures treated as nonfatal no-plugin mode, null `priv->stores` on reconfigure, stale inode context, inodelk leaks on unusual errors, blocking downloads in fop path, direct remote-read callback lifetime, and xdata ownership. Source snapshot has brace/duplicate-token oddities in `cs_truncate_cbk`. Tests should cover local and remote states for read/write/truncate, upload-complete setxattr, remote-read enabled/disabled, plugin absent, plugin hook missing, repair stat failure, concurrent recalls, and xattr cleanup after successful/failed download.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync.h -->
# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync.h

## Purpose
Public internal header for the cloudsync translator, defining state objects and prototypes shared by manual and generated fops.

## Important APIs, types, and functions
Defines `ALIGN_SIZE`, `CS_LOCK_DOMAIN`, `cs_dlstore`, `cs_inode_ctx_t`, and plugin descriptor `cs_plugin`. Declares core helpers for local initialization, locate/execute, resume paths, inodelk unlock, write callback, common callback, object-state checks, xattr callbacks, reading auth info, inode context update/get/reset, read/truncate resume functions, remote-read postprocess, and `cs_serve_readv`.

## Control flow
Generated C includes this header to call shared helpers, while `cloudsync.c` uses it to expose manual fops and plugin-related routines.

## State and persistence behavior
`cs_inode_ctx_t` caches object state per inode and includes loc/xattr metadata. Other declared state is transient.

## Dependencies and integration points
Includes `cloudsync-common.h` and generated `cloudsync-autogen-fops.h`, binding generated and manual sources together.

## Risks and test signals
Header cycles are possible because the generated header includes `cloudsync.h` in its template. Tests should compile from a clean generated state and verify all declared helpers have definitions or are intentionally external/generated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/compress/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/compress/Makefile.am

## Purpose
Top-level Automake file for the compress/CDD feature translator directory.

## Important APIs, types, and functions
Only `SUBDIRS = src` and empty `CLEANFILES`.

## Control flow
Recursive make descends to `src`.

## State and persistence behavior
No direct runtime state.

## Dependencies and integration points
Integrates the compression translator subtree into the GlusterFS build.

## Risks and test signals
Low risk; verify recursive build reaches `compress/src`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/compress/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/compress/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/compress/src/Makefile.am

## Purpose
Builds the `cdc.la` compression translator.

## Important APIs, types, and functions
Defines sources `cdc.c` and `cdc-helper.c`, headers `cdc.h` and `cdc-mem-types.h`, links against `libglusterfs` and `ZLIB_LIBS`, and installs the module under GlusterFS feature xlator directory.

## Control flow
Automake compiles the translator with zlib include flags, `_FILE_OFFSET_BITS=64`, `_GNU_SOURCE`, and GlusterFS RPC/libglusterfs include paths.

## State and persistence behavior
Build output is `cdc.so`; no runtime state here.

## Dependencies and integration points
Depends on zlib and GlusterFS xlator infrastructure. Runtime module is identified as `cdc` in `cdc.c`.

## Risks and test signals
Build risks center on zlib discovery and PIC/link flags. Tests should build with compression enabled and run read/write paths in client and server mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/compress/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/compress/src/cdc-helper.c -->
# sources/distributed-fs/glusterfs/xlators/features/compress/src/cdc-helper.c

## Purpose
Implements zlib compression/decompression helpers for the CDC translator, including iobuf allocation, gzip-compatible trailer handling, CRC validation, and debug dumping.

## Important APIs, types, and functions
Public functions are `cdc_compress()` and `cdc_decompress()`. Helpers include `cdc_next_iovec`, little-endian trailer put/get, `cdc_init_gzip_trailer`, `cdc_alloc_iobuf_and_init_vec`, `cdc_flush_libz_buffer`, `do_cdc_compress`, `cdc_check_content_for_deflate`, `do_cdc_decompress`, and validation routines.

## Control flow
Compression creates an iobref, ensures xdata exists, initializes deflate with configured window/mem/level, compresses each input iovec into output iobufs, flushes with `Z_FINISH`, appends an 8-byte trailer containing CRC and original size, sets the `deflate` canary in xdata, and optionally dumps a gzip-debug file. Decompression first checks the canary, requires a single input iovec, extracts trailer CRC/length, inflates into output iobufs, recomputes CRC across output vectors, validates length, and returns inflated byte count.

## State and persistence behavior
State is per-call in `cdc_info_t` and zlib stream structs. Persistent data on the wire is compressed payload plus 8-byte validation trailer and xdata canary; debug mode writes `/tmp/cdcdump.gz`.

## Dependencies and integration points
Depends on zlib, GlusterFS iobuf/iobref pools, logging, sys_write, and dictionary xdata from `cdc.c`.

## Risks and test signals
Risks include only partially supporting multi-iovec decompression, output `MAX_IOVEC` overflow, memory cleanup on mid-stream failures, trailer assumptions, and passthrough behavior when canary is missing. Tests should cover small/large buffers, corrupt CRC/length, multiple iovecs, min-size bypass, debug dump, and zlib init/flush failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/compress/src/cdc-helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/compress/src/cdc-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/features/compress/src/cdc-mem-types.h

## Purpose
Defines memory accounting tags for the CDC compression translator.

## Important APIs, types, and functions
Enum `gf_cdc_mem_types` defines tags for private state, vectors, gzip trailer, and range end.

## Control flow
`mem_acct_init()` in `cdc.c` registers `gf_cdc_mt_end`.

## State and persistence behavior
No persistence; affects memory diagnostics for CDC allocations.

## Dependencies and integration points
Includes GlusterFS common memory types and is used by `cdc.c` and `cdc-helper.c`.

## Risks and test signals
Low risk. Test memory accounting on compression/decompression paths, especially trailer allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/compress/src/cdc-mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/compress/src/cdc.c -->
# sources/distributed-fs/glusterfs/xlators/features/compress/src/cdc.c

## Purpose
Implements the `cdc` compression translator, wrapping `readv` and `writev` to compress in one deployment mode and decompress in the opposite mode.

## Important APIs, types, and functions
Primary fops are `cdc_readv` and `cdc_writev` with callbacks. Lifecycle functions are `init`, `fini`, and `mem_acct_init`. `cdc_priv_t` stores zlib window size, mem level, compression level, min size, mode, and debug flag.

## Control flow
`readv` winds to the child and transforms data in the callback: server mode compresses reads, client mode decompresses reads. `writev` transforms before winding: client mode compresses writes, server mode decompresses writes. If data length is zero, below `min-size`, or transform fails, it passes through the original vector. Init validates one child, reads options, normalizes zlib parameters, and requires `mode` to be either `client` or `server`.

## State and persistence behavior
Translator state is only `cdc_priv_t`. Persistent/wire-visible behavior is xdata canary plus compressed bytes/trailer when compression is applied; otherwise data passes through unmodified.

## Dependencies and integration points
Depends on zlib helpers in `cdc-helper.c`, GlusterFS stack APIs, iov length helpers, and xdata dictionaries. It must be paired client/server so the opposite side understands the canary and compression mode.

## Risks and test signals
Risks include transform failure silently passing through in many cases, mismatched client/server placement, compressed write path using original `iobref` while passing generated vectors, and invalid option handling. Tests should cover client-server round trips, server-client read path, min-size threshold, invalid modes/options, corrupted compressed data, and debug mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/compress/src/cdc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/compress/src/cdc.h -->
# sources/distributed-fs/glusterfs/xlators/features/compress/src/cdc.h

## Purpose
Declares CDC compression translator state, constants, macros, and helper APIs.

## Important APIs, types, and functions
Defines `cdc_priv_t`, `cdc_info_t`, vector macros, zlib defaults, client/server mode constants, min chunk size, validation trailer size, gzip OS id, canary key, debug dump path, mode string macros, and prototypes for `cdc_compress()` and `cdc_decompress()`.

## Control flow
`cdc.c` fills `cdc_info_t` per read/write operation and calls helper APIs declared here. Mode macros are used during initialization.

## State and persistence behavior
`cdc_priv_t` is translator lifetime state; `cdc_info_t` is per-operation state. Constants define the wire trailer and canary behavior.

## Dependencies and integration points
Includes GlusterFS xlator headers and zlib. Shared by main CDC translator and helper implementation.

## Risks and test signals
Risks include fixed `MAX_IOVEC` array in `cdc_info_t` and raw string mode comparison. Tests should cover vector count boundaries and option parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/compress/src/cdc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/gfid-access/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/gfid-access/Makefile.am

## Purpose
Top-level Automake file for the gfid-access feature translator directory.

## Important APIs, types, and functions
Only `SUBDIRS = src`.

## Control flow
Recursive make enters `src`.

## State and persistence behavior
No direct state.

## Dependencies and integration points
Integrates gfid-access into the GlusterFS feature translator build.

## Risks and test signals
Low risk; verify recursive build enters `gfid-access/src`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/gfid-access/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/gfid-access/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/gfid-access/src/Makefile.am

## Purpose
Builds the `gfid-access.la` feature translator.

## Important APIs, types, and functions
Defines source `gfid-access.c`, headers `gfid-access.h` and `gfid-access-mem-types.h`, installs under the feature xlator directory, and links against `libglusterfs`.

## Control flow
Automake compiles the translator with GlusterFS lib and RPC/XDR includes.

## State and persistence behavior
Build output is `gfid-access.so`; no runtime state in this Makefile.

## Dependencies and integration points
Part of GlusterFS xlator module build. The memory type header in this work item supports allocations in the implementation not listed here.

## Risks and test signals
Build risk is minimal; test by compiling the module and verifying install/uninstall paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/gfid-access/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/gfid-access/src/gfid-access-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/features/gfid-access/src/gfid-access-mem-types.h

## Purpose
Defines memory accounting tags for the gfid-access translator.

## Important APIs, types, and functions
Enum values reserve `gf_gfid_access_mt_priv_t`, `gf_gfid_access_mt_gfid_t`, and `gf_gfid_access_mt_end`.

## Control flow
The gfid-access implementation registers this range during memory-accounting initialization and uses the tags for private state and gfid allocations.

## State and persistence behavior
No durable state. It classifies allocations.

## Dependencies and integration points
Includes GlusterFS common memory type definitions and is compiled with `gfid-access.c`.

## Risks and test signals
The enum name is `gf_changelog_mem_types`, likely copied from another translator; this can confuse diagnostics but not necessarily compiled symbol behavior. Tests should check memory accounting names and compile warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/gfid-access/src/gfid-access-mem-types.h -->
