# sources/distributed-fs/orangefs/src/io/bmi/op-list.h

## Purpose
Declares the BMI operation-list API and search-key structure used by BMI method implementations.

## Important APIs, Types, And Functions
Defines `op_list_p` as `struct qlist_head *` and `struct op_list_search_key`, whose fields can optionally match method address, message tag, and operation id via `*_yes` switches. Declares list creation, add, cleanup, remove, dump, empty, next, count, and search functions.

## Control Flow
Callers create a list, append pending `method_op` objects, optionally search or inspect the first entry, remove completed entries, and finally clean up all remaining operations.

## State And Persistence
The header owns no state but defines the query contract for pending operation lists. It deliberately exposes quicklist-based list storage.

## Dependencies And Integration Points
Includes `pvfs2-internal.h`, `quicklist.h`, `bmi-types.h`, and `bmi-method-support.h`. It is shared by BMI core and methods such as `bmi_zoid`.

## Risks And Test Signals
Risks are ABI coupling to `method_op` and broad search-key fields that may not be meaningful for every method. Compile tests for BMI methods and queue behavior tests are the main signals.
