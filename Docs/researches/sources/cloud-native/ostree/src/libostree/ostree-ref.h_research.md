# sources/cloud-native/ostree/src/libostree/ostree-ref.h

## Purpose
This public header defines `OstreeCollectionRef`, the tuple type for globally identifying refs by optional collection ID plus ref name.

## Important APIs, State, and Integration
The struct exposes `gchar *collection_id` and `gchar *ref_name`. The API declares boxed type registration, constructor, duplication/free functions, hash/equality callbacks, vector duplication/free helpers, and the `OstreeCollectionRefv` auto-cleanup-friendly typedef. It integrates with collection-aware pull, summary, and ref APIs where a plain ref string is insufficient.

## Risks and Tests
Because fields are public, callers can mutate them after construction and bypass validation; hash-table users must treat keys as immutable. Tests should assert construction validation, transfer ownership, hash/equality consistency, and vector cleanup behavior.
