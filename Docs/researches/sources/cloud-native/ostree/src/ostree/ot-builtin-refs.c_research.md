# sources/cloud-native/ostree/src/ostree/ot-builtin-refs.c

## Purpose
Implements `ostree refs`, listing, creating, deleting, and aliasing refs, with optional revision output and collection-ref support.

## Important APIs, Types, And Functions
`ostree_builtin_refs()` dispatches per prefix/revision. `do_ref()` handles normal refs and aliases. `do_ref_with_collections()` handles collection refs. `collection_ref_cmp()` sorts collection refs. The implementation uses `ostree_repo_list_refs()`, `ostree_repo_list_refs_ext()`, `ostree_repo_set_ref_immediate()`, `ostree_repo_set_alias_ref_immediate()`, `ostree_repo_list_collection_refs()`, and `ostree_repo_set_collection_ref_immediate()`.

## Control Flow
The command parses options and, if arguments are provided, processes each as a prefix or existing revision. Delete and create modes enforce safer arity: deletes require at least one prefix and creates require exactly one existing revision. Normal listing loads refs or aliases, sorts names, and prints names, `name -> alias`, or `name<TAB>revision`. Create mode checks whether the new ref already exists, honors `--force`, parses the new refspec, and either creates an alias to an existing ref or resolves the source revision and writes a new ref. Delete mode lists matching refs, rejects deletion if a matching ref has an active alias, parses each refspec, and clears it. Collection mode lists, creates, or deletes collection refs, treating `collection:ref` syntax as an input convention for creation.

## State And Persistence
Listing is read-only. Create, alias, and delete persist ref changes immediately. The entry point aborts any repository transaction on exit, although these helpers use immediate ref APIs rather than explicit transactions.

## Dependencies And Integration Points
The command integrates normal refs, remote refspec parsing, alias refs, collection refs, revision resolution, and validation helpers. It is a key companion to commit, reset, pull, prune, and summary generation.

## Risks And Edge Cases
Collection create intentionally abuses refspec syntax by treating the left side as collection ID. Deleting a ref with active aliases fails to avoid dangling aliases. Alias creation cannot target remote refs and requires the target ref to exist. Existing directory conflicts during resolve are cleared so lower-level ref writing can handle them. Collection deletion lists with `OSTREE_REPO_LIST_REFS_EXT_NONE`, so remote and local behavior should be checked carefully.

## Test Signals
Tests should cover sorted listing, revision output, prefix filtering, alias listing/creation/replacement, delete rejection with aliases, forced create replacement, remote refspec parsing, collection ref listing/creation/deletion, invalid collection IDs, and safe errors for missing required prefixes.
