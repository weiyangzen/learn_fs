<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/linear_assignment_optimizer.h -->
# sources/distributed-fs/lizardfs/src/common/linear_assignment_optimizer.h

## Purpose
Implements the Bertsekas auction algorithm with epsilon scaling for square integer maximization assignment problems. The source was read completely for this report.

## Important APIs, Types, And Functions
`linear_assignment::auctionOptimization` overloads and `detail::auctionStep` are the main APIs. Inputs are fixed-size matrix-like containers and `std::array<int,N>` assignment outputs.

## Control Flow
For size 0/1 it returns directly. For larger sizes it scales every matrix value by `size+1`, initializes prices, repeatedly runs auction steps with decreasing epsilon, then finalizes with epsilon 1.

## State And Persistence Behavior
No persistence. It mutates the input value matrix in place and writes assignment/object-assignment arrays.

## Dependencies And Integration Points
Depends only on standard containers/algorithms/asserts. Used where chunk/data placement needs optimal pairings.

## Risks And Edge Cases
In-place scaling is surprising and can overflow for large values. Assertions enforce assumptions only in debug builds; release builds rely on sane size and value ranges.

## Test Signals
`linear_assignment_optimizer_unittest.cc` compares random cases up to size 10 against brute-force optimum and covers size 1.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/linear_assignment_optimizer.h -->
