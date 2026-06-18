# File Research: sources/block-storage/mdadm/dlink.h

## Purpose
`dlink.h` declares and macro-defines mdadm's hidden-header doubly linked list API.

## Contents
It defines `struct __dl_head`, allocation macros `dl_alloc`, `dl_new`, `dl_newv`, accessor macros `dl_next` and `dl_prev`, and function prototypes for list creation, insertion, deletion, freeing, initialization, and string duplication.

## Integration Notes
The macros require `xcalloc()` to be visible in the including compilation unit.
