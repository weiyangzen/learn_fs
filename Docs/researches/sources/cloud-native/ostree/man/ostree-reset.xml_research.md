# sources/cloud-native/ostree/man/ostree-reset.xml

Purpose: documents `ostree reset`, which resets a ref to another commit/revision.

Important APIs/types: required `REF` and `REF_TO_RESET_TO`; examples use parent revision syntax `my-branch^`.

Control flow: resolves the target revision and updates the named ref to point at it.

State and persistence: mutates repository ref state but does not delete now-unreachable objects by itself.

Dependencies and integration: integrates rev parsing, refs, log, and later prune/cleanup for object reclamation.

Risks and test signals: risks include destructive history movement and unreachable commits. Signals are log before/after reset and fsck/prune behavior after reset.
