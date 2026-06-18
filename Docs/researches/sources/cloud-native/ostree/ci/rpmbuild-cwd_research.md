# sources/cloud-native/ostree/ci/rpmbuild-cwd

Purpose: wrapper for `rpmbuild` that maps all RPM build directories to the current working directory, matching Fedora's local packaging pattern.

Important APIs/functions: captures `pwd` and `exec`s `rpmbuild` with `_sourcedir`, `_specdir`, `_builddir`, `_srcrpmdir`, `_rpmdir`, and `_buildrootdir` definitions.

Control flow: no branching; replaces the shell process with `rpmbuild` and forwards all arguments.

State and persistence: RPM sources, build output, SRPMs, RPMs, and `.build` buildroot are written under the invocation directory.

Dependencies and integration: used by RPM/Packit CI scripts where tarball and spec live in one directory.

Risks and test signals: risks are workspace pollution and accidental overwrite of RPM products. Signal is that `rpmbuild-cwd -bs ostree.spec` emits all products locally.
