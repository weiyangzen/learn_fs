# sources/distributed-fs/ceph-client/net/netfilter/nft_objref.c

Purpose: implements nftables `objref` expressions that invoke named stateful objects directly or select objects from object maps.

Important APIs/types/functions: immediate mode stores a `struct nft_object *` in expression private data and `nft_objref_eval()` calls `obj->ops->eval()`. `nft_objref_map` stores an object set, key source register, and binding; `nft_objref_map_eval()` looks up a set element, falls back to catchall, extracts `nft_set_ext_obj()`, and evaluates that object. `nft_objref_validate_obj_type()` applies special hook/family validation for synproxy objects.

Control flow: select_ops chooses map mode if set source register plus set name/id are present, or immediate mode if object name/type are present. Immediate init looks up the object by name/type in the next generation and increments its use count; activate/deactivate restore/decrement use around transactions. Map init looks up an object set, validates `NFT_SET_OBJECT`, parses the key register, and binds the set. Map lifecycle activates/deactivates/destroys the set binding.

State/persistence: expression state holds object refs or set bindings. Runtime object state is owned by the target object type. Dependencies include nft object registry, set lookup exported by `nft_lookup.c`, catchall object maps, transaction use counters, and synproxy hook constraints. Risks include use-count imbalance, object type mismatch in maps, missing catchall causing `NFT_BREAK`, and validation gaps for object types with hook restrictions. Test signals: immediate counter/quota/limit object references, object map lookup and catchall, synproxy validation, transaction rollback, object deletion while referenced, invalid set/object types, and dump round trip.
