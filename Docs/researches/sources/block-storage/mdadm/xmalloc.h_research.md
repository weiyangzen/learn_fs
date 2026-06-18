# File Research: sources/block-storage/mdadm/xmalloc.h

## Purpose
Header for mdadm fail-fast allocation helpers.

## Contents
Declares:
- `xmalloc`
- `xrealloc`
- `xcalloc`
- `xstrdup`
- `xmemalign`

## Integration
Included by mdadm modules that use fatal allocation wrappers.
