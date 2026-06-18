# sources/distributed-fs/orangefs/src/io/bmi/reference-list.c

## Purpose
Manages BMI address reference records that map public `BMI_addr_t` values, string ids, method addresses, and method operation tables.

## Important APIs, Types, And Functions
Public functions are `ref_list_new`, `ref_list_add`, `ref_list_search_addr`, `ref_list_search_method_addr`, `ref_list_search_str`, `ref_list_rem`, `ref_list_cleanup`, `alloc_ref_st`, and `dealloc_ref_st`. Private state is the global string hash table `str_table`; private comparison logic is `ref_list_compare_key_entry`.

## Control Flow
`ref_list_new` enforces a single live reference list by refusing to create a second global hash table. `alloc_ref_st` allocates/zeros a reference and registers it with the safe id generator to assign `bmi_addr`. `ref_list_add` adds id strings to the hash and links the record into the list. Searches either use `id_gen_safe_lookup`, `method_addr->parent`, or the string hash. Removal unlinks the list/hash entry without freeing it. Cleanup deallocates all records, finalizes the hash table, and frees the list.

## State And Persistence
State is entirely in-memory: a quicklist of references, a global string hash table, id-generator registrations, owned `id_string` memory, and method-address ownership through `interface->set_info(BMI_DROP_ADDR, method_addr)`. No disk persistence exists.

## Dependencies And Integration Points
Uses `quickhash`, `quicklist`, `id-generator`, BMI method support, and method-specific `set_info` cleanup. It is the BMI glue layer between user-visible addresses and transport-specific address records.

## Risks And Test Signals
Risks include the singleton hash table, no internal locking, cleanup calling method code during reference destruction, `ref_list_search_method_addr` assuming `map->parent` is valid, and partial allocation leaks if future code changes add more owned fields. Tests should cover add/search/remove by all keys, duplicate list creation failure, string hash cleanup, method address drop behavior, and id-generator unregister behavior.
