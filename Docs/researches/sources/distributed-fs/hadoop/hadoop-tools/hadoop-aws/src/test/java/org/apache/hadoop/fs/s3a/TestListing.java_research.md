# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestListing.java

## Purpose

Narrow unit test for the listing helper that converts provided `S3AFileStatus` arrays into `RemoteIterator` instances.

## Important APIs, Types, and Functions

The file constructs an `S3AFileStatus` and calls `Listing.toProvidedFileStatusIterator()`, then uses `RemoteIterator.hasNext()` and `next()`.

## Control Flow

The test creates a one-element status array, obtains the iterator, verifies `hasNext()` before reading, checks the first returned element is the original status, verifies the iterator is exhausted, and asserts another `next()` raises `NoSuchElementException`.

## State, Dependencies, and Integration Points

State is only the in-memory iterator cursor. The test depends on `AbstractS3AMockTest`, `S3AFileStatus`, `Path`, and LambdaTestUtils exception interception.

## Risks and Test Signals

This protects iterator contract behavior for list implementations. It is small but catches off-by-one or invalid exhausted-iterator behavior that can affect callers consuming S3A listings.
