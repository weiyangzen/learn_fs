# sources/distributed-fs/openafs/src/opr/casestrcpy.c

Purpose: small string utilities for case conversion and bounded string composition.

Important APIs/types/functions: `lcstring` copies lowercased text with forced NUL termination; `ucstring` copies uppercased text; `stolower` lowercases a string in place; `strcompose` concatenates a NULL-terminated varargs list into a bounded buffer.

Control flow: conversion helpers copy until `n` bytes or source NUL. `strcompose` starts with an empty buffer, tracks remaining capacity, and returns NULL if any component would exceed the buffer.

State and persistence: caller-provided buffers only; no global or persistent state.

Dependencies/integration: exposed through macro-renamed names in `afs/opr.h` (`opr_lcstring`, etc.). Uses ctype and string functions.

Risks and test signals: ctype functions receive `char` values directly; negative signed chars can be undefined outside ASCII. `strcompose` returns without `va_end` on early overflow, which is a cleanup correctness issue. Unit tests should cover exact buffer limits and case conversion.
