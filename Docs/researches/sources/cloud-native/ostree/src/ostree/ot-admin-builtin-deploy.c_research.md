<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-deploy.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtin-deploy.c

## Purpose
Implements `ostree admin deploy`, creating a new deployment from a ref/revision with optional staging, finalization locking, origin override, kernel argument control, initrd overlays, and retention policy.

## Important APIs and Types
Exports `ot_admin_builtin_deploy`. Options include `--os/--stateroot`, `--origin-file`, `--no-prune`, `--no-merge`, `--retain*`, `--stage`, `--lock-finalization`, `--not-as-default`, kernel argument replace/append/delete/proc/none flags, and `--overlay-initrd`. It uses `OstreeKernelArgs`, `OstreeSysrootDeployTreeOpts`, `OstreeDeployment`, and sysroot deploy/stage/write APIs.

## Control Flow
After parsing and validating incompatible options, locking implies staging. The command resolves the requested ref, determines a merge deployment unless disabled, performs initial cleanup, builds optional kernel args, stages overlay initrds and records checksums, then either stages the tree or deploys immediately. Non-staged deployments are written into the deployment list with retention/default flags. It finishes with prepare cleanup for staged/no-prune cases or full sysroot cleanup otherwise.

## State and Persistence
Mutates sysroot deployments, origin files, kernel argument bootconfig, overlay initrd staging data, staged-finalization lock state, bootloader deployment order, and repository cleanup state. With `--lock-finalization`, it also writes a legacy runstate lockfile for compatibility.

## Dependencies and Integration Points
Uses `ostree-sysroot-private.h`, repo rev resolution, sysroot deploy/stage APIs, kernel arg helpers, libglnx fd helpers, and admin shared functions. It is central to admin workflows and interacts with bootloader and shutdown finalization services.

## Risks
Option interaction is complex: staged deployments reject some retention/default flags, `--no-merge` and karg deletion conflict, and karg defaults depend on merge state. Partial failures can leave staging data, so cleanup ordering is important. Overlay initrd checksums must remain aligned with staged/deployed metadata. Finalization locks require compatibility between new deployment metadata and legacy lockfile behavior.

## Test Signals
Coverage should include immediate deploy, staged deploy, locked staged deploy, origin-file input, all kernel-arg modes and conflicts, overlay initrd staging, retain/pending/rollback flags, no-prune cleanup behavior, and recovery from partial deploy failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-deploy.c -->
