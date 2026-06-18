<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/Makefile-decls.am -->
## sources/cloud-native/ostree/Makefile-decls.am

### Purpose
This fragment initializes shared automake variables and helper hook targets used by all other non-recursive make fragments.

### APIs, Types, and Control Flow
It resets common accumulators such as `AM_CPPFLAGS`, `AM_CFLAGS`, `SUBDIRS`, `BUILT_SOURCES`, `CLEANFILES`, install program/script/library lists, introspection lists, schema lists, and OSTree boot install variables. It includes `buildutil/glib-tap.mk` to initialize test handling. It defines aggregate hook targets `install-data-hook: $(INSTALL_DATA_HOOKS)` and `all-local: $(ALL_LOCAL_RULES)`.

### State, Dependencies, and Integration
It is included early by top-level `Makefile.am`, so later fragments append to initialized variables. The hook accumulators let fragments add install/all behavior without overriding each other.

### Risks and Test Signals
Ordering matters: including this after fragments would erase their additions. Test signals are automake generation, successful hook chaining, and tests being recognized through `glib-tap.mk`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/Makefile-decls.am -->
