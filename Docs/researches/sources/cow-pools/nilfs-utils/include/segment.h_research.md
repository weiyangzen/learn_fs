# File Research: sources/cow-pools/nilfs-utils/include/segment.h

Internal segment iteration API. It defines iterators for partial segments, file records inside segment summaries, and block descriptors inside file records.

The header declares error classes for malformed partial segments and file summaries, iteration functions, string conversion for errors, and loop macros. It is used by `dumpseg` and the GC library to interpret raw segment summaries safely.
