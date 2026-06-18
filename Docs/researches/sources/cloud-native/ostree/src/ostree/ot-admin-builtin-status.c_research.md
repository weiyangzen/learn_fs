<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-status.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtin-status.c

## Purpose
Implements `ostree admin status`, listing deployments in text, JSON, verification, or default-state forms.

## Important APIs and Types
Exports `ot_admin_builtin_status`. Options are `--verify`, `--json`, `--skip-signatures`, and `--is-default`. Helpers `deployment_print_status` and `deployment_write_json` read deployment metadata, origin refspec, commit metadata, signature state, unlocked/pinned/staged/finalization/soft-reboot flags, and pending/rollback classification.

## Control Flow
The command loads the sysroot and repo, obtains deployments and booted/pending/rollback references, then either emits a JSON object with a `deployments` array, prints `default`/`not-default`, prints `No deployments.`, or iterates deployments in text form. Text mode loads commit metadata best-effort, prints version/origin/unlocked/pinned/status markers, optionally prints GPG signatures, and optionally verifies signatures. JSON mode requires commit load for each deployment and writes fields through `ul_jsonwrt`.

## State and Persistence
No persistent state is modified. It reads deployment files, origin keyfiles, commit objects, detached metadata, and remote GPG configuration.

## Dependencies and Integration Points
Depends on libglnx, OSTree repo/sysroot/deployment APIs, optional GPGME/signature verification, and `ul-jsonwrt` for JSON output. Status output is often consumed by automation.

## Risks
Text mode tolerates commit load failure for display, but JSON mode treats commit load as fatal. Signature output depends on origin remote and remote GPG config. JSON field names are a compatibility surface for scripts. `--is-default` reports error when not in a booted OSTree system.

## Test Signals
Tests should cover empty deployments, booted/pending/rollback/staged/locked/soft-reboot/pinned/unlocked flags, JSON parse and schema fields, signature display and skip/verify modes, originless deployments, and default detection.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-status.c -->
