<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader.h -->
# sources/cloud-native/ostree/src/libostree/ostree-bootloader.h

## Purpose
Declares the internal bootloader interface contract.

## Important APIs and Types
Defines `OstreeBootloaderInterface` with vfuncs `query`, `get_name`, `write_config`, optional `post_bls_sync`, and optional `is_atomic`. Declares type/cast macros, autoptr cleanup, type getter, and dispatch helpers.

## Control Flow
No implementation flow in the header; it defines the backend contract.

## State and Persistence
State is backend-specific. The interface methods operate over bootversion, deployment arrays, cancellables, and errors.

## Dependencies and Integration Points
Includes `<ostree.h>` and `otutil.h`. Concrete bootloader headers include this file and sysroot deployment code calls the dispatch helpers.

## Risks
`write_config` receives `GPtrArray *new_deployments`; backend assumptions about length and ordering must match sysroot deployment orchestration. Atomicity reporting is critical for safe bootversion switching.

## Test Signals
Compile/type checks, backend interface conformance, and orchestration tests that call through dispatch helpers validate this header.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader.h -->
