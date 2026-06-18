# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-combine.h

Purpose: declares answer-combination helpers used by EC fop managers and callbacks.

Important APIs/types: `EC_COMBINE_DICT` and `EC_COMBINE_XDATA` select dictionary sources; `ec_combine_f` is the fop-specific comparator/merger callback. Exported functions cover iatt rebuild/combine, dictionary compare/combine, vector/flock/statvfs comparison or merge, generic callback combination, and write-fop combination.

Control flow and integration: callbacks allocate `ec_cbk_data_t`, populate fop-specific fields, then call `ec_combine(cbk, combine_func)`. Managers later call `ec_fop_prepare_answer()`, which uses `ec_dict_combine()` on the selected best callback. This header depends on EC callback/fop types from `ec-types.h` through includers.

State behavior: the interface mutates callback data in place, especially masks, counts, dictionaries, and iatt arrays. No persistent storage is owned here. Risks include passing the wrong `which` selector, using `NULL` combine functions for fops that need fop-specific validation, and header include-order assumptions because it does not include `ec-types.h` itself. Test signals include compile coverage for all includers and unit-style callback combination tests for every exported comparator.
