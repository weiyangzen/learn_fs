# sources/distributed-fs/openafs/src/aklog/Makefile.in

## Purpose

`Makefile.in` defines the automake/autoconf-era build rules for OpenAFS `aklog`-related command-line tools. It builds `aklog`, `asetkey`, `klog`, and `akeyconvert`, sets Kerberos compiler/linker flags, links against OpenAFS internal libraries, and installs client and server administration binaries into the correct bindirs.

## Important variables and targets

The file includes generated configuration fragments from `src/config/Makefile.config` and `src/config/Makefile.pthread`. `MODULE_CFLAGS` adds Kerberos CPP flags and `-DALLOW_REGISTER`; `MODULE_LDFLAGS` adds Kerberos linker flags. `AKLIBS` combines generic libs, Kerberos ldflags/libs, and configured `@AKLOG_KRB5_LIBS@`. `AFSLIBS` collects ptserver, rxkad, cmd, opr, and util libtool archives. `KCLIBS` collects auth, cmd, and opr libraries for `akeyconvert`. `LT_libs` carries hcrypto and roken dependencies.

`SRCS`/`OBJS` describe the common `aklog` object set. The `all` target builds `aklog`, `asetkey`, `klog`, and `akeyconvert`. Each program target invokes `$(LT_LDRULE_static)`, so these tools are linked through the repository's libtool static-linking convention. `install` installs `aklog` and `klog.krb5` to `${bindir}` and `asetkey` plus `akeyconvert` to `${afssrvbindir}`. `dest` mirrors that behavior into OpenAFS staging paths. `clean` removes libtool output, objects, and built binaries.

## Control flow and integration

This file is consumed by the OpenAFS configure/build system. Substitution variables such as `@srcdir@`, `@TOP_OBJDIR@`, `@KRB5_CPPFLAGS@`, and `@AKLOG_KRB5_LIBS@` are filled during configuration. Build order is target-driven: object compilation rules come from included config makefiles, while this file specifies final link lines and install locations.

## State and persistence behavior

The makefile creates transient object files and binaries in the build tree and installs selected binaries into destination prefixes. It has no runtime state. `clean` is intentionally local to this directory and removes the known products.

## Dependencies

The rules depend on Kerberos 5, hcrypto, roken, pthread settings, OpenAFS internal libraries, and libtool helper macros. `akeyconvert` links against auth/cmd/opr rather than the broader ptserver/rxkad/util set used by `aklog`, `asetkey`, and `klog`.

## Risks and test signals

The `all` target builds `akeyconvert`, but `install` and `dest` list only `aklog asetkey klog` as prerequisites while still installing `akeyconvert`. A parallel or direct `make install` from a clean tree could attempt to install `akeyconvert` without first building it unless make reaches it through another dependency. Link-order regressions are another risk because Kerberos and OpenAFS static libraries can be order-sensitive. Test signals include clean `make all`, clean `make install DESTDIR=...`, clean `make dest DEST=...`, and configure variants with different Kerberos/com_err providers.
