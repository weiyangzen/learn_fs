# sources/distributed-fs/lizardfs/src/common/intrusive_list.h

Purpose: implements a non-owning doubly linked intrusive list for nodes deriving from `intrusive_list_base_hook`.

Important APIs/types/functions: `intrusive_list_base_hook` stores `prev_node_` and `next_node_`; `intrusive_list_iterator` provides bidirectional iteration; `intrusive_list<Node>` exposes front/back, push/pop, dispose variants, clear, erase, insert, swap, iterators, and whole-list `splice`.

Control flow: list operations directly rewrite hooks inside user-owned nodes. Dispose variants remove nodes then call a supplied disposer. `splice` inserts all nodes from another list before a position and empties the source.

State and persistence: list stores only front/back pointers and size; node linkage lives inside nodes. No ownership, persistence, or synchronization.

Dependencies and integration: depends on standard iterator/type traits and `platform.h`. Useful where allocation overhead of `std::list` is undesirable.

Risks: nodes must not be inserted into multiple lists or destroyed while linked. The list destructor does not unlink or delete elements. Assertions catch only some misuse. Iterator comparisons include ordering operators that compare raw addresses, not list order.

Test signals: `intrusive_list_unittest.cc` covers push_back, erase, insert, splice, and disposal cleanup.
