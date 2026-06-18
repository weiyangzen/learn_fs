# sources/distributed-fs/openafs/src/gtx/keymap.c

Purpose: implements the GTX keymap trie and key-processing state machine.

Important functions: `keymap_Create`, `gtx_CopyString`, internal `BindIt`, `keymap_BindToString`, `keymap_Delete`, `keymap_InitState`, `keymap_ProcessKey`, and `keymap_ResetState`.

Control flow and state: binding walks each character in a command string, creating submaps for prefixes and installing a proc entry at the final character. Binding with a `NULL` proc deletes the final entry. Processing checks the current map slot: empty resets and returns `-1`; submap advances state; proc invokes the callback with runtime rock and entry rock, then resets.

Dependencies and integration: included by frames and tests. Callback signatures match frame/input usage: `(void *runtime, void *entry_rock)`.

Risks: no allocation failure check after `keymap_Create` inside submap creation before passing to `BindIt`; `BindIt` stores submap pointers through `void *aproc`; refcount is unused. `keymap_BindToString` silently succeeds for empty strings. Test signals should cover prefix maps, deletion, invalid key values, duplicate replacement freeing old names, and recursive map deletion.
