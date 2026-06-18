## sources/distributed-fs/orangefs/src/client/webpack/d.authn/Makefile.am

Purpose: Automake recipe for building and installing the Apache `mod_authn_orangefs` authentication module.

Important APIs, types, and functions: Sets `AM_CPPFLAGS` with version/provider defines, Apache/APR include paths, OrangeFS cflags, PVFS source include roots for common, security, BMI, trove, proto, and I/O description headers. `AM_LDFLAGS` uses `pvfs2-config --libs`. Builds `libmod_authn_orangefs.la` from `mod_authn_orangefs.c`; custom install invokes `apxs -i -a -n authn_orangefs`.

Control flow: The subdir builds one libtool module and installs/enables it through Apache's extension tool.

State and persistence: Build artifacts and Apache installed module/config activation persist after install.

Dependencies and integration points: Requires Apache `apxs`, APR headers, OrangeFS installed libraries, and PVFS source internals for authentication/security code.

Risks and test signals: Like the admin module, it depends on source-tree internal headers and a custom install target rather than standard Automake install behavior. Test compile with current PVFS source layout, Apache module load, install under non-root/staging workflows, and provider-name/version strings.
