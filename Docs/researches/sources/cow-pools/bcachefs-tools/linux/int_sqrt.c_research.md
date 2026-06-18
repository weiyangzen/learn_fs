# File Research: sources/cow-pools/bcachefs-tools/linux/int_sqrt.c

Implements integer square root using shift-and-subtract, returning floor sqrt. On 32-bit builds it also provides `int_sqrt64()` for 64-bit inputs.
