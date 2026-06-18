# sources/distributed-fs/alluxio/underfs/web/src/main/java/alluxio/underfs/web/WebUnderFileSystem.java

## Purpose
`WebUnderFileSystem` is a read-only HTTP/HTTPS UFS. It treats web URLs as files or directory listings, reads content via HTTP GET, and parses HTML directory indexes with Jsoup.

## APIs and Control Flow
Unsupported mutating or connection operations throw `IOException` with a shared unsupported message. `exists` uses `HttpUtils.head`. `getBlockSizeByte`, `getFileStatus`, and `getDirectoryStatus` rely on `getStatus`. Private `getStatus(path, fileName)` reads HEAD headers for content length and last modified, computes an approximate content hash for files, and returns file or directory status based on `isFile`. `isDirectory` checks `Content-Type` for `text/html`, downloads the page, and compares the `<title>` text against configured directory-title markers. `listStatus` downloads HTML, finds anchor elements, skips from configured parent markers, resolves relative links, and obtains statuses for each link. `open` gets an input stream and skips the requested offset.

## State, Dependencies, and Integration
State is limited to configured HTTP timeout and unsupported-operation text. Dependencies include `ConsistentUnderFileSystem`, Alluxio status/options classes, `HttpUtils`, `ByteStreams`, Jsoup, Apache HTTP headers, and web-specific configuration keys for timeout, title matching, parent names, and last-modified format.

## Risks and Test Signals
`isFile` calls `isDirectory`, so status checks can issue HEAD plus GET requests and may misclassify arbitrary HTML files as directories based on title text. `listStatus` builds relative URLs with `path + "/" + href`, which can double slashes or mishandle `../`/absolute-root links. Live tests depend on external network availability and remote HTML layout.
