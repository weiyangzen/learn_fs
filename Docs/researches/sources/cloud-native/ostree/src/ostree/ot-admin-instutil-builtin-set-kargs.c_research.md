<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-instutil-builtin-set-kargs.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-instutil-builtin-set-kargs.c

## Purpose
Implements deprecated installer utility `ostree admin instutil set-kargs`, setting kernel command-line arguments on the first deployment.

## Important APIs and Types
Options include `--import-proc-cmdline`, `--merge`, `--replace`, and `--append`. Uses `OstreeKernelArgs` and `ostree_sysroot_deployment_set_kargs`.

## Control Flow
The command parses superuser/unlocked context, requires at least one deployment, creates a fresh kargs object, optionally imports `/proc/cmdline` or merges previous deployment options, applies replacement and append arrays, appends positional args, converts to string vector, and writes kargs to the first deployment.

## State and Persistence
Mutates bootconfig kernel arguments for the first deployment in the sysroot.

## Dependencies and Integration Points
Uses sysroot deployment list, bootconfig parser, kernel arg helpers, and installer command dispatch.

## Risks
The command targets only the first deployment. `--import-proc-cmdline` overrides merge behavior by design. Deprecated status means newer karg paths may differ.

## Test Signals
Tests should cover merge vs proc import, replace and append precedence, positional args, no deployment error, and resulting bootconfig options.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-instutil-builtin-set-kargs.c -->
