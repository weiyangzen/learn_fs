# sources/distributed-fs/orangefs/src/io/bmi/reference-list.h

## Purpose
Defines BMI reference-record structure and declares reference-list management helpers.

## Important APIs, Types, And Functions
Defines `ref_list_p`, `struct ref_st`, and `ref_st_p`. `ref_st` stores `BMI_addr_t`, id string, method address, BMI method ops pointer, list link, reference count, and hash link. Declares creation, add, address/method/string searches, removal, cleanup, allocation, and deallocation helpers.

## Control Flow
Consumers allocate `ref_st`, fill string/method/interface fields, add it to a list, search by desired key, remove on address drop, and deallocate when no longer referenced.

## State And Persistence
The header defines the in-memory shape of address references. The `ref_count` field signals intended shared ownership, although increments/decrements are not implemented in this file.

## Dependencies And Integration Points
Includes BMI types, method support, quicklist, and quickhash. It also works around a Windows `interface` macro by renaming the field under `WIN32`.

## Risks And Test Signals
Risks are structure-field drift against BMI core, ambiguous ownership of `method_addr`, and unused or externally managed `ref_count`. Build coverage across Windows and non-Windows plus address lifecycle tests are useful signals.
