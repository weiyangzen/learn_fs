# sources/cloud-native/ostree/src/libotutil/ot-gpg-utils.h

## Purpose
Declares GPGME helper APIs and cleanup macros for GPGME objects.

## Important APIs, Types, And Functions
Defines auto cleanup functions for `gpgme_data_t`, `gpgme_ctx_t`, and `gpgme_key_t`. Declares error translation, temporary homedir setup, GIO stream data adapters, context creation, agent cleanup, and WKD URL generation.

## Control Flow
No implementation flow beyond cleanup macro definitions. Consumers can use `g_auto` with GPGME types to ensure release functions run.

## State And Persistence Behavior
No state in the header. Declared APIs can create temporary homedirs and manage GPGME resources.

## Dependencies And Integration Points
Depends on libglnx, GIO, and GPGME. It is included by GPG verification and key-management code.

## Risks
Cleanup macros require correct null sentinel handling. GPGME type ownership must match whether functions return borrowed or owned handles.

## Test Signals
Compile tests with `g_auto` declarations and implementation tests for declared functions are relevant.
